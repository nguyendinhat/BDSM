import bpy

#=======[Test]======
mode_items = [
    ("EDGE", "Along Edge", ""),
    ("NORMAL", "Along Normal", "")
]


#=======[PUNCHit]======
ctrl = ['LEFT_CTRL', 'RIGHT_CTRL']
alt = ['LEFT_ALT', 'RIGHT_ALT']
shift = ['LEFT_SHIFT', 'RIGHT_SHIFT']
numbers = ['ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'ZERO',
           'NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4', 'NUMPAD_5', 'NUMPAD_6', 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9', 'NUMPAD_0']
input_mappings = {'ONE': "1",
                  'TWO': "2",
                  'THREE': "3",
                  'FOUR': "4",
                  'FIVE': "5",
                  'SIX': "6",
                  'SEVEN': "7",
                  'EIGHT': "8",
                  'NINE': "9",
                  'ZERO': "0",

                  'NUMPAD_1': "1",
                  'NUMPAD_2': "2",
                  'NUMPAD_3': "3",
                  'NUMPAD_4': "4",
                  'NUMPAD_5': "5",
                  'NUMPAD_6': "6",
                  'NUMPAD_7': "7",
                  'NUMPAD_8': "8",
                  'NUMPAD_9': "9",
                  'NUMPAD_0': "0",

                  'BACK_SPACE': "",
                  'DELETE': "",
                  'PERIOD': ".",
                  'COMMA': ".",
                  'MINUS': "-",

                  'NUMPAD_PERIOD': ".",
                  'NUMPAD_COMMA': ".",
                  'NUMPAD_MINUS': "-"}
extrude_mode_items = [('AVERAGED', 'Averaged', 'Extrude along Averaged Face Normals'),
                      ('EDGE', 'Edge', 'Extrude along any chosen Edge of any Object'),
                      ('INDIVIDUAL', 'Individual', 'Extrude along Individual Vertex Normals')]