import json

from bfcl.model_handler.oss_model.base_oss_handler import OSSHandler
class customHandler(OSSHandler):
    def __init__(self, model_name, temperature) -> None:
        super().__init__(model_name, temperature)
    
    def _format_prompt(self, message, function):
        formatted_prompt = "<|begin_of_text|>"
        system_prompt = ''
        remaining_message =message
        if message[0]['role'] == 'system':
            system_prompt = message[0]['content'].strip()
            remaining_message = message[1:]
        formatted_prompt += "<|start_header_id|>user<|end_header_id|>\n\n"
        prompt = f"""Based on the question, you must make one or more function/tool calls to achieve the purpose. If none of the functions can be used, point it out. If the given question lacks the parameters the function requires, also point it out. You should only return the function call in the tools call sections. The expected functions have the following format:
        {{
            "name": "function_name",
            "description": "function description",
            "parameters": {{
                "type": "dict",
                "properties": {{
                    "parameter1_name": {{
                        "type": "parameter type",
                        "description": "The description of the parameter"
                        }},
                        "parameter2_name": {{
                            "type": "parameter type",
                            "description": "parameter description"
                            }}
                        }}
                    }}
        }}
        If you decide to invoke any of the function(s), you MUST strictly put it in the format of:
        {{
            "name": "function_name",
            "parameters": {{
                "parameter1_name": [parameter1_value],
                "parameter2_name": [parameter2_value]
                }}
            }}
        Here is a list of functions in JSON format that you can invoke: {function} <|eot_id|> """

        formatted_prompt += system_prompt + prompt
        if remaining_message[0]['role'] == 'user':
            formatted_prompt+= '<|start_header_id|>user<|end_header_id|>' + remaining_message[0]['content'].strip()
        else:
            formatted_prompt+= '<|start_header_id|>user<|end_header_id|>' + message[1]['content'].strip() + '<|eot_id|>'
        formatted_prompt+= '<|start_header_id|>assistant<|end_header_id|>'
        return formatted_prompt
    def decode_ast(self, result, language="Python"):
        result = result.replace('<|python_tag|>', '')
        if ';' in result:
            function_calls = result.split(';')
            function_calls = [json.loads(func_call) for func_call in function_calls]
        else:
            function_calls = eval(result)
            if type(function_calls) == dict:
                function_calls = list(function_calls)
        decoded_output = []
        for func_call in function_calls:
            name = func_call['function_name']
            params = func_call['parameters']
            decoded_output.append({name:params})
        return decoded_output
    def decode_execute(self, result):
        result = result.replace('<|python_tag|>', '')
        if ';' in result:
            function_calls = result.split(';')
            function_calls = [json.loads(func_call) for func_call in function_calls]
        else:
            function_calls = eval(result)
            if type(function_calls) == dict:
                function_calls = list(function_calls)
        decoded_output_executable = []
        for func_call in function_calls:
            name = func_call['name']
            params = func_call['parameters']
            decoded_output_executable.append(f"{name}({','.join([f'{k}:{repr(v)}' for k, v in params.items()])})")
        return decoded_output_executable
    
    
        
        
        
