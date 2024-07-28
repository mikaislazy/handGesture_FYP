# EdTech Application for learning Taoism and Buddhism gesture - Tutorial Mode
This project aims to develop a application for learning Taoism and Buddhism gesture.The interface folder contains the interface The model contain the training information of the model. 
There are 9 hand gestures for learning in total, where the user can choose the knowledge task and the recognition task in each hand gesture. Also, they can practice difference different hand gesture in customized order and combination in the practice tool.
Please run the application on MACOS

## Requirements
- Python 3.9.5
- Pyqt5 5.15.10
- pytest 8.2.1
- OpenCV 4.6.0
- Tensorflow 2.13.0
- MediaPipe 0.9.1.0
  
## Run the application
```
cd interface/Widgets 
python main.py
```
## Run the testcase
```
cd interface
python test_runner.py
# the db will be cleared after the test
```
## Install the environment using Anaconda
```
cd set-up-env
conda env create -f UI-env.yml
```

## Project Structure
```
handGesture_FYP
├─ .gitignore
├─ README.md
├─ interface
│  ├─ Test
│  │  ├─ __init__.py
│  │  ├─ test_handGestureComponent.py
│  │  ├─ test_handGestureKnowledge.py
│  │  ├─ test_handGesturePractice.py
│  │  ├─ test_handGestureRecognition.py
│  │  └─ test_handGestureTaskSelection.py
│  ├─ Widgets
│  │  ├─ Keypoint
│  │  │  ├─ __init__.py
│  │  │  ├─ analyse_keypoint_utils.py
│  │  │  ├─ common_utils.py
│  │  │  ├─ constants.py
│  │  │  ├─ extract_keypoints.py
│  │  │  ├─ mean_of_normalized_keypoints.json
│  │  │  └─ normalise_keypoints.py
│  │  ├─ Model
│  │  │  ├─ VGGModel.py
│  │  │  └─ __init__.py
│  │  ├─ UserData
│  │  │  └─ db_utils.py
│  │  │  ├─ handGesture
│  │  │  ├─ handGestureBtn
│  │  │  └─ otherBtn
│  │  ├─ other
│  │  │  ├─ answer.json
│  │  │  ├─ frames
│  │  │  │  ├─ fire_effect
│  │  │  │  ├─ lighting_effect
│  │  │  │  └─ thunder_effect
│  │  │  │     
│  │  │  ├─ method.json
│  │  │  └─ question.json
│  │  ├─ main.py
│  │  ├─ mainComponents.py
│  │  ├─ gesture_constants.py
│  │  ├─ handGestureComponent.py
│  │  ├─ handGestureKnowledge.py
│  │  ├─ handGesturePractice.py
│  │  ├─ handGesturePracticeTool.py
│  │  ├─ handGestureRecognition.py
│  │  ├─ handGestureTaskSelection.py
│  │  ├─ images
│  │  ├─ system.py
│  │  ├─ tool.py
│  │  ├─ userPerformance.py
│  │  └─ utils.py
│  └─ test_runner.py
├─ model
│  ├─ overall_dataset.json
│  ├─ trainingModel.ipynb
│  └─ utils.py
└─ set-up-env
   └─ UI-env.yml

```

### Resources:
The effect is from Free B-Roll by <a href="http://videezy.com/">Videezy.com</a>
