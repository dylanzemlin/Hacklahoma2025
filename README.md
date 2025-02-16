## Inspiration

This year's theme was all about making technology that worked for you, preferably in the background. For us this meant something that was hands-off, that you could interact with without having to press a bunch of buttons. We really wanted to do a wearable device this year, because they're cool, and fit the theme very well (ex. Fitbit). The inspiration for {{INSERT NAME HERE}} came from the line in the theme about fostering human connection between individuals.

> Create technology that helps us
use technology less. Your project
might help accelerate
workflows/tasks, **foster human
connection**, or develop alternative
versions of apps that respect our
attention. (emphasis added)


## What it does

{{INSERT NAME HERE}} allows for easier communication between the hearing impaired and their peers. It is a wearable device (could be a necklace, could be added to a hat, etc.) that translates American Sign Language (ASL) to text on a screen, and then from text to speech. This allows someone who has no knowledge of sign language to hold a conversation with someone who does.


## How we built it

We used AkramOM606's American-Sign-Language-Detection repository to get a neural network, as well as a bunch of training data for the model. We modified this to add custom hand signs for signaling when you were done signing your words, to trigger the text-to-speech.

now running the model is resource-intensive, which is why we do it off-site.

this necessitated some networking to send data from the raspberry pi to a computer with a large GPU, run the model, and send it and back.

we use Tailscale for easy networking n' stuff.

something something we used TensorFlow and OpenCV to do AI/ML. Big Data. Python.


## Challenges we ran into
 - Adding the custom thumbs-up/thumbs-down gestures to the model. There was actually an interesting problem we tracked down with original repsitory's code, which required us to downgrade tensorflow because the model needed to be translated to TFLite, which was dropped in the latest version.
 - networking. always networking. sockets n' stuff. some of it was python, some was C++.
 - drawing on the LCD?
 - Originally we wanted to see if we could use a microcontroller instead of a full-blown raspberry pi to send the camera frames, to make the final device smaller and lighter, but we could not get it to deliver good video quality.


## Accomplishments that we're proud of

 - the fact that it actually works
 - that we actually got the ASL stuff to work
 - that the networking works


## What we learned

ASL to English
Drawing on an LCD display
Working with a model


## What's next for {{INSERT NAME HERE}}

{{INSERT NAME HERE}} has quite a few improvements that could be made to it over time.
- Swap to an improved processor to do onboard ASL translation and voice to text.
- Redesign the enclosure to be a smaller form factor
- Add a onboard speaker to the enclosure
- do it the other way (speech to text) so the hearing impaired can read off the screen instead of reading lips
- make the voice used for the text-to-speech customizable