init python:
    import sys
    import os

    # Path to your python_modules folder
    custom_path = os.path.join("python_modules")
    from AIChatRenpy import AIChat
    chat = AIChat(preprompt_key="cliffhanger")
    