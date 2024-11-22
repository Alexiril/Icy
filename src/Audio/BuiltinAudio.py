""""""

from queue import Queue
from typing import Any
from wave import Wave_read

from pyaudio import PyAudio

# Too hard to make typings stubs.
from sounddevice import RawInputStream, query_devices  # type: ignore
from termcolor import colored  # type: ignore

from src import State
from src.Interfaces import AudioInterface


class BuiltinAudio(AudioInterface):
    """"""

    state: State | None
    _output_finished: bool
    _input_stream: RawInputStream
    _recording: bool
    _recording_queue: Queue[bytes]

    def __init__(self) -> None:
        self.state = None
        self._output_finished = False
        self._recording = False
        device_info: dict[str, Any] = query_devices(kind="input")  # type: ignore
        self.samplerate = device_info["default_samplerate"]
        self._input_stream = RawInputStream(
            samplerate=self.samplerate,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=self._chunk_callback,
        )
        self._input_stream.start()
        self._recording_queue = Queue()
        return

    def before_start(self, state: State) -> None:
        self.state = state
        self._output_finished = False
        return

    def output(self, data: Wave_read) -> None:
        if self.state is None:
            raise RuntimeError("Audio output was called without before start handler")
        self._output_finished = False
        chunk: int = 8000
        audio = PyAudio()
        stream = audio.open(
            format=audio.get_format_from_width(data.getsampwidth()),
            channels=data.getnchannels(),
            rate=data.getframerate(),
            output=True,
        )
        while (b := data.readframes(chunk)) and not self.state.get(
            self.force_stop_handler, False
        ):
            stream.write(b)
        stream.stop_stream()
        stream.close()
        audio.terminate()
        self._output_finished = True

    def _chunk_callback(self, indata: Any, frames: Any, time: Any, status: Any) -> None:
        if status:
            text = f'Sound device status updated: {status}'
            print(colored(text, "red"))
        if not self._recording:
            return
        self._recording_queue.put(bytes(indata))

    def input(self) -> bytes:
        return self._recording_queue.get()

    def output_finished(self) -> bool:
        return self._output_finished

    def clear_input_queue(self) -> None:
        self._recording_queue = Queue()

    def start_recording(self) -> None:
        self.clear_input_queue()
        self._recording = True

    def stop_recording(self) -> None:
        self._recording = False

    def terminate(self) -> None:
        self._input_stream.close()
