# ASLTalk

ASLTalk is a real-time, browser-based American Sign Language (ASL) communication and handshape translation application. It converts trained ASL handshapes into spoken phrases, supports follow-up conversations, and provides speech-to-text replies for the hearing participant.

## Tech Stack

**Languages and markup:** HTML5, CSS3, JavaScript, Python.

**Frontend and UI:** Tailwind CSS, Responsive Web Design, Canvas API, HTML5 Video, Material Symbols, Progressive Web App (PWA) styles and metadata.

**AI/ML and computer vision:** MediaPipe Tasks Vision, MediaPipe Hand Landmarker, WebAssembly, normalized 21-point hand landmarks, a Python nearest-neighbor handshape classifier, and a judge-safe camera-free demo mode.

**Backend and data:** Python standard-library HTTP server, JSON, REST-style HTTP endpoints, Local Storage, Session Storage, and JSON sample persistence through the Python server.

**Browser APIs:** MediaDevices API, Camera/getUserMedia API, Web Speech API, Web Speech Recognition API, Speech Synthesis API, Screen Wake Lock API, Vibration API, Service Worker API, Canvas API, Fetch API, and Web Storage APIs.

**Application capabilities:** Offline-style asset caching with a service worker, PWA manifest support, camera switching, screen wake lock, flashlight controls where supported, conversation history, guided handshape training, sample import/export, follow-up prompts, speech output, speech recognition, and vibration feedback.

## Architecture

1. The browser captures a live camera stream through the MediaDevices and getUserMedia APIs.
2. MediaPipe Hand Landmarker detects hand landmarks and converts them to 21 normalized hand points.
3. The browser sends the normalized landmark vector to the Python AI server.
4. The Python nearest-neighbor classifier compares the vector with trained ASL samples and returns the label, confidence, and distance.
5. The recognized handshape is matched to a context-specific phrase.
6. The browser shows a confirmation step before speaking the phrase.
7. Web Speech Recognition handles the hearing participant's voice, while Speech Synthesis speaks translated text.

The browser is the primary interface and camera runtime. Python is the primary AI/ML classification and server-side sample-storage component. JavaScript remains responsible for UI behavior, MediaPipe landmark extraction, camera and speech integration, and demo presentation controls.

## Judge Demo

ASLTalk includes a camera-free **Quick Start Demo** for presentations and judge testing. It provides deterministic pharmacy, hospital, and follow-up communication scenarios while preserving the confirmation-before-speech requirement.

The demo is intentionally separate from live recognition. It does not claim to measure or validate ASL recognition accuracy.

## Current Accuracy Scope

The live model recognizes seven static context-specific handshapes through MediaPipe landmarks and a nearest-neighbor classifier trained from user samples. It does not recognize complete ASL, fingerspelling sequences, facial grammar, movement, or sentence-level signing.

No production accuracy figures are claimed until multiple participants have provided samples and an evaluation script produces verified metrics. A single presenter should not be treated as proof of cross-user performance.

## Run Locally

Requires Python 3. Open a terminal in the project directory:

```powershell
python ai_server.py
```

Then open:

`http://127.0.0.1:8000`

Camera, microphone, speech recognition, and wake-lock features may require HTTPS in some browsers. Localhost and `127.0.0.1` are trusted for development in browsers that support those requirements.

## Workflow: First Use to Conversation

Use Chrome or Microsoft Edge for the most reliable camera, speech recognition, and demo experience.

### 1. Start ASLTalk

1. Install Python 3 and open a terminal in the ASLTalk project folder.
2. Run `python ai_server.py`.
3. Wait for the message that the server is running at `http://127.0.0.1:8000`.
4. Open that address in Chrome or Microsoft Edge.
5. Keep the terminal running while using the app.

### 2. Allow Device Permissions

1. When the browser asks for camera access, select **Allow**.
2. Keep the full hand visible with good front lighting.
3. If voice replies are needed, allow microphone access when prompted.
4. Use a supported browser if speech recognition or microphone controls do not appear.

The video feed is processed locally by MediaPipe. Microphone speech is converted through the browser's speech-recognition service where supported.

### 3. Choose a Situation

Use one of the context buttons:

- **Pharmacy** for prescriptions and medication questions.
- **Hospital** for urgent or medical care communication.
- **Bank** for account and transaction questions.
- **Shop** for shopping and payment questions.

Each context maps the seven supported handshapes to a short, contextual sentence.

### 4. Try the Judge-Safe Demo First

For a presentation or first test:

1. Select **Quick Start Demo** at the bottom-right corner.
2. Choose a pharmacy, hospital, medication, water, or pain scenario.
3. Review the proposed phrase.
4. Select **Speak it** to speak the phrase or select **Try again** to cancel.
5. Continue with voice or typed replies.

Demo mode works without recognizing a live handshape and does not require live training. It is designed for dependable demonstrations.

### 5. Train the Seven Live Handshapes

Training is optional for demo mode but required for live camera recognition.

1. Select a context.
2. Press **G** to open guided training.
3. Follow the countdown for each handshape.
4. Keep each hand shape visible and move it slightly during the three-second recording period.
5. Complete all seven handshapes before closing the training panel.

The supported handshapes are:

1. **1 — ONE:** Point the index finger upward while curling the other fingers.
2. **2 — TWO:** Point the index and middle fingers upward in a V shape.
3. **3 — THREE:** Extend the thumb, index finger, and middle finger.
4. **4 — FOUR:** Extend all four fingers while holding the thumb against or across the palm.
5. **5 — FIVE:** Open the palm with all five fingers spread.
6. **W:** Face the palm forward and extend the index, middle, and ring fingers; tuck the thumb against the curled pinky.
7. **Y:** Extend the thumb and pinky while curling the index, middle, and ring fingers.

During live recording, you can also hold the number keys **1–7** to add samples. Release the key when finished recording that handshape.

For the best training results:

- Use a plain background.
- Keep the camera at chest or face level.
- Use even lighting.
- Avoid moving outside the camera frame.
- Train in the same location and camera position used for recognition.
- Keep the palm orientation consistent.
- Add more samples if a handshape is frequently misclassified.

Training status is reset only when samples are cleared or removed. Samples are stored in browser Local Storage and synchronized with the Python server.

### 6. Recognize a Handshape

1. Finish guided training or add enough samples for the active context.
2. Hold the intended handshape steady.
3. Wait for the system to display the handshape and confidence.
4. Keep holding until the confirmation dialog appears.
5. Review the proposed phrase before continuing.

Hold the handshape stable instead of moving quickly. Low-confidence recognition is rejected rather than converted into an unintended message.

### 7. Confirm or Correct the Phrase

When the confirmation dialog appears:

- Select **Speak it** to speak the proposed sentence.
- Select **Edit phrase** to change the proposed text before speaking.
- Select **Try again** to reject recognition and return to live tracking.
- Cancel or close the dialog to stop a proposed phrase.

For an editable phrase, select **Edit phrase**, replace the text directly inside the confirmation card, and then select **Speak it**. Pressing **Speak it** both speaks and saves the edited text for that context and handshape. For example, an edited Hospital handshape 4 phrase will be used again whenever Hospital mode and handshape 4 are presented, including camera recognition and judge-safe demo controls.

Press **T** to open the training and phrase panel. Each of the seven handshapes has an editable phrase field. Change a field and select **Save phrase**; that mapping is marked **(edited)** and remains stored for the selected context and handshape until changed or reset. Press **Reset** beside one mapping to restore only that default, or press **R** to reset every edited phrase.

The T-panel scrolls vertically, so all seven mappings remain accessible on small screens and phones. Use the wheel, trackpad, touch scroll, or panel scrollbar to move from handshape 1 to handshape 7.

Custom mappings are stored in browser Local Storage and remain available after refresh. They apply to both live recognition, confirmation, Quick Start Demo controls, and the T-panel for the matching mode.

Default mappings:

| Handshape | Pharmacy | Hospital | Bank | Shop |
|---|---|---|---|---|
| 1 | Pick up prescription | I need a doctor | Check account balance | Ask product cost |
| 2 | Medicine safety | I am in pain | Make a deposit | Find an item |
| 3 | Dose timing | I need an ASL interpreter | Withdraw money | Ask for another size |
| 4 | Pay by card | Help communicating with the care team | Speak with a manager | Pay by card |
| 5 | Thank you | I need a bathroom | Thank you | Thank you |
| W | I need water | I need water | Pay with cash | Show another option |
| Y | Call my doctor | Call my family | Call when ready | Find the nearest exit |

### 8. Respond by Voice or Text

1. Tap the microphone button to let the hearing person reply by voice.
2. Wait for speech recognition to display the final response.
3. If voice recognition is unavailable, select **Type Reply**.
4. Enter a short response and select **Send & Speak**.

The conversation appears in the history area and can be replayed where the interface supports it.

### 9. Use Follow-Up Questions

Hospital and other context-specific flows may ask a follow-up question. Answer with the appropriate trained handshape displayed in the prompt banner.

Examples:

- **ONE** may identify chest pain.
- **TWO** may identify throat pain.
- **THREE** may identify head pain.
- **FOUR** may identify stomach pain.
- **FIVE** may identify cough or cold.

Select **Skip** if the follow-up should not continue.

### 10. Use Face-to-Face Mode

1. Select **Face-to-face**.
2. The top **Staff View** is for the pharmacist, nurse, receptionist, or other hearing staff. It displays the deaf patient's confirmed signed phrase.
3. The bottom-left **Deaf Patient Camera** is the signer side. Show the selected handshape here and keep it steady until the confirmation is reviewed.
4. The bottom-right **Patient View — Staff Response** displays staff replies as large text. Staff can reply by tapping **Staff: tap to reply by voice** or selecting **Staff: type a reply**.
When a recognized handshape opens the confirmation card, its proposed phrase is copied immediately into the Face-to-face staff text panel. If the signer edits the phrase before speaking, the staff text updates with the edited phrase. Speech is sent only after the signer confirms it.
When staff selects **Type Reply**, the typed text is forwarded to the Patient View only after staff selects **Send & Speak**. Voice replies are forwarded through the existing hearing display as soon as speech recognition returns their text.
5. The recognition camera is deliberately on the patient side only; face-to-face mode does not replace the live confirmation and does not guess a phrase.
6. Select **Rotate staff view** when the staff person needs an upside-down-facing staff panel in a shared-device setup.
7. Select **Exit** when finished.

### 11. Manage Training and Settings

Training shortcuts:

- **T** — Open or close the training panel.
- **G** — Start guided training for all seven handshapes.
- **1–7** — Hold the matching key while recording live samples.
- **E** — Export samples as JSON.
- **I** — Import a previously exported sample file.
- **X** — Clear all recorded samples.
- **Escape** — Close overlays or end follow-up mode.

Open settings to control vibration, visual flashing, speech output, and larger text.

### 12. Complete a Demo in Three Minutes

1. Open ASLTalk and confirm the Python and browser status.
2. Select **Pharmacy**.
3. Select **Quick Start Demo**.
4. Choose medicine pickup.
5. Review the phrase and select **Speak it**.
6. Show the typed-reply or microphone flow.
7. Return to the hospital context.
8. Run one follow-up scenario such as stomach pain.
9. Close the demo with a clear limitation: ASLTalk currently recognizes seven contextual handshapes, not complete ASL.

## Python AI API

- `GET /api/health` - Returns the server health and Python language status.
- `GET /api/config` - Returns classifier scope and privacy configuration.
- `GET /api/samples` - Returns persisted training samples.
- `POST /api/predict` - Classifies a 42-value normalized landmark vector.
- `POST /api/sample` - Adds a handshape training sample.
- `POST /api/samples` - Saves or replaces the complete training sample set.
- `DELETE /api/samples` - Clears persisted training samples.

## Submission Tags

Python, JavaScript, HTML, CSS, HTML5, Tailwind CSS, MediaPipe Hand Landmarker, MediaPipe Tasks Vision, WebAssembly, AI, ML, Computer Vision, nearest-neighbor classifier, REST API, Python HTTP server, JSON, PWA, Progressive Web App, Service Worker, Web APIs, Web Camera API, MediaDevices API, getUserMedia, Canvas API, Web Speech API, Web Speech Recognition API, Speech Synthesis API, Screen Wake Lock API, Vibration API, Local Storage, Session Storage, Responsive Web Design, browser-app.
