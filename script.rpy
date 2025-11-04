label start:
    play music "regret.mp3" loop
    image movie = Movie(size=(1920, 1080), xpos=0, ypos=0, xanchor=0, yanchor=0)
    play movie "videos/cliffhanger.webm" loop
    show movie at zoom_in
    "Un froid glacial s'engouffre sur la falaise..."
    "Le vent hurle à travers les rochers, emportant avec lui les derniers vestiges de chaleur."
    show movie at zoom_default
    "Un homme se tient là, face à l'abîme, son manteau battant au rythme des bourrasques."
    show verso grin at right, active with dissolve
    $renpy.pause(2.0)    
    verso "C'est donc ici que tout doit se {b}terminer{/b}..."
    $renpy.pause(1.0)   
    verso "Après tout ce que j'ai traversé, je me retrouve seul, au bord du vide."
    show verso sad at right, active with dissolve
    verso "Et en regardant en bas, je vois les nuages prêts à m'accueillir."
    $renpy.pause(1.0) 

    python:
        reponse = renpy.input("Intervenir...", length=200)
        answer = chat.talk("Recto : "+ reponse).replace("Verso : ","").replace("Recto : ","")
    show recto happy at left with dissolve
    show verso sad at right, inactive
    recto "[reponse]"
    show recto happy at left, inactive
    hide verso sad
    show verso sad at right, active
    verso "[answer]"
    return
