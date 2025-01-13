import gradio as gr
import inspect
from typing import get_origin, Union, Any
from PIL import Image


class FunctionWrapper:
    def __init__(self, func):
        self.func = func
        self.interface = self.create_gradio_interface(func)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def process_inputs(self, *args):
        processed_args = [None if arg == "" else arg for arg in args]
        return self.func(*processed_args)

    def create_gradio_interface(self, func):
        sig = inspect.signature(func)
        params = sig.parameters

        def get_input_component(param):
            default_value = param.default if param.default is not param.empty else None
            if param.name == "region_name":
                default_value = "us-east-1"

            if param.annotation == str:
                return gr.Textbox(label=param.name, value=default_value)
            elif param.annotation == int:
                return gr.Number(label=param.name, value=default_value or None)
            elif param.annotation == bool:
                return gr.Checkbox(label=param.name, value=bool(default_value))
            else:
                return gr.Textbox(label=param.name, value=default_value)

        def get_output_component(return_annotation):
            if return_annotation == str:
                return gr.Textbox()
            elif return_annotation == dict[str, Any] or return_annotation == dict[str, list[str]]:
                return gr.JSON()
            elif return_annotation == float:
                return gr.Number()
            elif return_annotation == Image.Image:
                return gr.Image()
            elif return_annotation == list:
                return gr.JSON()
            else:
                return gr.Textbox()

        inputs = [get_input_component(param) for param in params.values()]
        return_annotation = sig.return_annotation
        if get_origin(return_annotation) is Union or get_origin(return_annotation) is list:
            return_annotation = return_annotation.__args__[0]
        outputs = [get_output_component(return_annotation)]
        if get_origin(return_annotation) is tuple:
            outputs = [get_output_component(type_) for type_ in return_annotation.__args__]

        iface = gr.Interface(
            fn=self.process_inputs,
            inputs=inputs,
            outputs=outputs,
            live=False
        )
        return iface

    def create_url(self):
        self.interface.launch(share=True)