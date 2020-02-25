from easygui import *
import image_paste as im

while 1:
    greeting = """
    Welcome to the Impresys ultra-simple image bulk pasting tool.
    Would you like to insert many images into a single background image,
    or insert a single image into many different images?
    """
    greeting_title = "Impresys bulk pasting tool"
    greeting_choices = [
        "Wrap many images in larger background (shelling)",
        "Insert smaller image into many larger images (insertion)"
    ]
    choice = choicebox(greeting, greeting_title, choices=greeting_choices)
    choice = 'shell' if choice==greeting_choices[0] else 'insert'
    print(choice)
    if choice == 'shell': # --> USER SELECTED SHELLING
        image_field_msg = """
            Enter the location of the .demo file as well as the image used for
            background/shelling. Enter the location on the background where the assets
            should be located (measured from the top left corner), and their final dimensions after being resized.
        """
        image_fields=[
            ".demo file location:",
            "Background (shelling) image file location:",
            "Asset image placement (x, pixels):", #where on BG image assets will be placed going right from top left
            "Asset image placement (y, pixels):", #where on BG image assets will be placed going down from top left
            "Assets final size (width, pixels):", #how wide should asset final size be counting from the x position specified
            "Assets final size (height, pixels):", #how tall should asset final size be counting from the y position specified
            "Apply to sections with title containing: (leave blank for all sections)",
        ]
    else: # --> USER SELECTED INSERTION
        image_field_msg = """
            Enter the location of both the .demo file as well as the image to be inserted
            onto the assets. Enter the location on the assets where the image to be inserted
            should be located (measured from the top left corner), and its final dimensions after being resized.
        """
        image_fields=[
            ".demo file location:",
            "Insertion image file location:",
            "Insert image placement (x, pixels):",
            "Insert image placement (y, pixels):",
            "Insert image final size (width, pixels):",
            "Insert image final size (height, pixels):",
            "Apply to sections with title containing: ('All' for all sections)"
        ]
    vals = [None, None, None, None, None, None, "All"]
    vals = multenterbox(image_field_msg,  title="Enter image data:",  fields = image_fields, values=vals)
    im.image_paste(vals[0], vals[1], (int(vals[2]), int(vals[3])), (int(vals[4]), int(vals[5])), choice, vals[6])