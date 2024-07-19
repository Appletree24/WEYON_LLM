import re

text = """
Action1: some_action
Action1 Input1: some_input
Action2: some_other_action
Action2 Input2: some_other_input
"""

# pattern = r"Action\s*\d*\s*:\s*(.*?)\s*Action\s*\d*\s*Input\s*\d*\s*:\s*(.*)"
pattern = r"Action\s*\d*\s*:[\s]*(.*?)[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
# pattern = r"行动\s*\d*\s*：[\s]*(.*?)[\s]*行动\s*\d*\s*输入\s*\d*\s*：[\s]*(.*)"
matches = re.findall(pattern, text)

for match in matches:
    action, action_input = match
    print(f"Action: {action}")
    print(f"Input: {action_input}")
