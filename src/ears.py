import speech_recognition as sr
import logging
import numpy as np
from src.utils.config_loader import load_config

class Ears:
    def __init__(self):
        self.config = load_config()
        self.backend = self.config['ears']['backend']
        self.whisper_model = None
        
        logging.info(f"Initializing Ears with backend: {self.backend.upper()}")

        if self.backend == 'whisper':
            try:
                from faster_whisper import WhisperModel
                w_config = self.config['ears']['whisper']
                logging.info(f"Loading Faster-Whisper model ('{w_config['model_size']}' on {w_config['device']})...")
                self.whisper_model = WhisperModel(
                    w_config['model_size'], 
                    device=w_config['device'], 
                    compute_type=w_config['compute_type']
                )
                
                # WARMUP: Force a dummy transcription to trigger any lazy-loading DLL errors immediately
                logging.info("Warming up model to verify CUDA...")
                dummy_audio = np.zeros(16000, dtype=np.float32) 
                self.whisper_model.transcribe(dummy_audio, beam_size=1)
                
                logging.info("Model loaded successfully.")
            except ImportError:
                logging.error("faster-whisper not installed. Please pip install faster-whisper.")
                raise
            except Exception as e:
                # Catch lazy loading errors here
                if "cublas" in str(e).lower() or "library" in str(e).lower():
                    logging.warning(f"CUDA Error detected during warmup: {e}")
                    logging.warning("Falling back to CPU...")
                    try:
                        self.whisper_model = WhisperModel(
                            w_config['model_size'], 
                            device="cpu", 
                            compute_type="int8" # often better for CPU
                        )
                        logging.info("Model loaded on CPU successfully.")
                    except Exception as cpu_e:
                        logging.error(f"Failed to load on CPU as well: {cpu_e}")
                        raise cpu_e
                else:
                    logging.error(f"Failed to load Faster-Whisper: {e}")
                    raise e

        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone(sample_rate=16000) # Whisper likes 16kHz, Google is fine with it
        
        logging.info("Calibrating microphone for ambient noise...")
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        logging.info("Calibration complete.")

    def listen(self, timeout=None):
        """
        Listens to the microphone and returns the transcribed text.
        """
        try:
            with self.mic as source:
                logging.info("Listening...")
                # phrase_time_limit ensures we don't get stuck listening forever
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                logging.info("Audio captured. Processing...")
            
            if self.backend == 'whisper':
                return self._transcribe_whisper(audio)
            else:
                return self._transcribe_google(audio)

        except sr.WaitTimeoutError:
            logging.info("Listening timed out.")
            return None
        except Exception as e:
            logging.error(f"Error in Ears: {e}")
            return None

    def _transcribe_whisper(self, audio):
        # Convert AudioData to numpy array (16kHz, mono, float32)
        audio_data = np.frombuffer(audio.get_raw_data(), np.int16).flatten().astype(np.float32) / 32768.0
        
        try:
            logging.info("Starting Whisper transcription (GPU)...")
            segments, _ = self.whisper_model.transcribe(audio_data, beam_size=5)
            logging.info("Transcription returned generator. Iterating...")
            text = " ".join([segment.text for segment in segments]).strip()
            logging.info(f"Heard (Whisper): '{text}'")
            return text
        except Exception as e:
            if "cublas" in str(e).lower() or "library" in str(e).lower():
                logging.warning(f"CUDA Error during transcription: {e}")
                logging.warning("Attempting runtime fallback to CPU...")
                try:
                    w_config = self.config['ears']['whisper']
                    self.whisper_model = None # Clear old model
                    
                    # Import here just in case, though already imported
                    from faster_whisper import WhisperModel
                    logging.info("Initializing Whisper on CPU...")
                    self.whisper_model = WhisperModel(
                        w_config['model_size'], 
                        device="cpu", 
                        compute_type="int8"
                    )
                    logging.info("Model re-loaded on CPU. Retrying transcription...")
                    
                    # Retry
                    segments, _ = self.whisper_model.transcribe(audio_data, beam_size=5)
                    text = " ".join([segment.text for segment in segments]).strip()
                    logging.info(f"Heard (Whisper-CPU): '{text}'")
                    return text
                    
                except Exception as cpu_e:
                    logging.error(f"Runtime CPU fallback failed: {cpu_e}")
                    return None
            else:
                logging.error(f"Whisper Transcription Error: {e}")
                return None

    def _transcribe_google(self, audio):
        try:
            text = self.recognizer.recognize_google(audio)
            logging.info(f"Heard (Google): '{text}'")
            return text
        except sr.UnknownValueError:
            logging.warning("Google Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            logging.error(f"Could not request results from Google Speech Recognition service; {e}")
            return None
