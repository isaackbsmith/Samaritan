import audioop
import pvporcupine
import pyaudio
import struct
import wave
import collections
import time
import os
import logging
import yaml

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.level = logging.DEBUG


class WakewordDetector:
    def __init__(self, config={"LISTEN": True}) -> None:
        self.level_history = collections.deque(maxlen=50)
        if config:
            self.config = config

    def get_score(self, data: bytes):
        score = audioop.rms(data, 2)
        self.level_history.append(score)
        level = 0
        for item in self.level_history:
            level += item
        return level / len(self.level_history)

    def save_message(self):
        """
        Save the message stored in self.recorded_data to a timestamped file.
        """
        filename = f"output{str(int(time.time()))}.wav"
        message_data = b''.join(self.recorded_data)

        # Use wave to save the message_data
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.stream.get_sample_size(
            self.stream.get_format_from_width(16 / 8)))
        wf.setframerate(self.detector.sample_rate)
        wf.writeframes(message_data)
        wf.close()
        logger.debug(f"finished saving: {filename}")
        return filename

    def terminate(self):
        """
        Terminate audio stream. system can call start() again to detect.
        :return: None
        """
        self.stream.terminate()
        self.audio_stream.close()
        self.detector.delete()
        self.running = False

    def detect(
        self,
        detected_callbackk=None,
        interrupt_check=None,
        sleep_time=0.03,
        silence_count_threshold=15,
        audio_recorder_callback=None,
        recording_timeout=100
    ):
        """
        Start the voice detector. For every `sleep_time` second, it checks the
        audio buffer for triggering keywords. If keyword is detected, then call
        corresponding function in `detected_callback`, which can be a single
        function (single model) or a list of callback functions (multiple
        models). Every loop also calls `interrupt_check` -- if it returns
        True, then breaks from the loop and return.
        :param detected_callback: a function or list of functions. The number of
                                  items must match the number of models in
                                  `decoder_model`.
        :param interrupt_check: a function that returns True if the main loop
                                needs to stop.
        :param float sleep_time: how much time in second every loop waits.
        :param audio_recorder_callback: if specified, this will be called after
                                        a keyword has been spoken and after the
                                        phrase immediately after the keyword has
                                        been recorded. The function will be
                                        passed the name of the file where the
                                        phrase was recorded.
        :param silence_count_threshold: indicates how long silence must be heard
                                       to mark the end of a phrase that is
                                       being recorded.
        :param recording_timeout: limits the maximum length of a recording.
        :return: None
        """
        self.running = True
        state = "PASSIVE"

        try:
            self.detector = pvporcupine.create(
                access_key="AzYbcpNhYVTRVeRS8T12tSDKCZNMtT3cl3Vw6CPm1LzBklz0LYVtgQ==",
                keywords=["jarvis", "computer"],)
            self.stream = pyaudio.PyAudio()
            self.audio_stream = self.stream.open(
                rate=self.detector.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.detector.frame_length
            )
        except Exception as e:
            print(e)

        if interrupt_check():
            logger.debug("Detect voice return")
            return

        while self.running:
            audio_data = self.audio_stream.read(self.detector.frame_length)
            if len(audio_data) == 0:
                time.sleep(sleep_time)
                continue

            avg_noise = self.get_score(audio_data)
            data = struct.unpack_from(
                "h" * self.detector.frame_length, audio_data)
            status = self.detector.process(data)

            if state == "PASSIVE":
                if status >= 0:
                    self.recorded_data = []
                    self.recorded_data.append(audio_data)
                    silence_count = 0
                    recording_count = 0
                    message = f"Wakeword {status} detected at: "
                    message += time.strftime("%Y-%m-%d %H:%M:%S",
                                             time.localtime(time.time()))
                    logger.info(message)
                    self.config["AVG_NOISE"] = avg_noise
                    self.terminate()

                    if detected_callbackk is not None:
                        detected_callbackk()

                    if audio_recorder_callback is not None:
                        state = "ACTIVE"
                    continue

            elif state == "ACTIVE":
                stop_recording = False
                recording_count = 0
                silence_count = 0

                if recording_count > recording_timeout:
                    stop_recording = True
                elif status == -1:
                    if silence_count > silence_count_threshold:
                        stop_recording = True
                    else:
                        silence_count = silence_count + 1
                elif status == 0:
                    silence_count = 0

                if stop_recording:
                    file_name = self.save_message()
                    audio_recorder_callback(file_name)
                    state = "PASSIVE"
                    continue

                recording_count = recording_count + 1
                self.recorded_data.append(audio_data)

        logger.debug("Done")
