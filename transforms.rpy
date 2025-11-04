init:
    transform active:
        alpha 1.0
        linear 0.5

    transform inactive:
        alpha 0.7
        matrixcolor TintMatrix("#000")
        linear 0.5

    transform transparent:
        alpha 0.5

    transform zoom_default:
        zoom 1# Original size
        # Ensures the anchor point is the center of the screen for better zooming
        xalign 0.5 
        yalign 0.5
            
    transform zoom_in:
        zoom 3 # 50% larger (adjust this value as needed)
        xalign 0
        yalign 0.2