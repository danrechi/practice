import json
import uuid
from datetime import datetime
from pathlib import Path
from io import BytesIO

import streamlit as st
import pandas as pd
from PIL import Image
from ultralytics import YOLO

HISTORY_FILE = Path(__file__).parent / "history.json"

# 2 = car, 3 = motorcycle, 5 = bus, 7 = truck
VEHICLE_CLASS_IDS = [2, 3, 5, 7]


@st.cache_resource
def load_model():
    model = YOLO("yolov8m.pt")
    return model


def process_image(uploaded_file, model):
    image = Image.open(uploaded_file)
    
    results = model.predict(image, imgsz=1280, conf=0.25, iou=0.5)
    
    car_count = 0
    result = results[0]  
    
    if result.boxes is not None:
        for box in result.boxes:
            class_id = int(box.cls[0])
            if class_id in VEHICLE_CLASS_IDS:
                car_count += 1
    
    annotated_image = result.plot(line_width=1)
    annotated_image = annotated_image[:, :, ::-1]

    return annotated_image, car_count


def save_to_history(data_dict):
    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []
    
    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        **data_dict
    }
    
    history.append(record)
    
    # Write back to file
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def load_history():
    if not HISTORY_FILE.exists():
        return pd.DataFrame()
    
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
        
        if not history:
            return pd.DataFrame()
        
        df = pd.DataFrame(history)
        
        df = df.rename(columns={
            "timestamp": "Date/Time",
            "filename": "File Name",
            "total_spaces": "Total Parking Spaces",
            "detected_cars": "Cars Detected",
            "free_spaces": "Free Spaces",
            "occupancy_percentage": "Occupancy Percent"
        })
        
        display_columns = [
            "Date/Time", "File Name", "Total Parking Spaces",
            "Cars Detected", "Free Spaces", "Occupancy Percent"
        ]
        
        return df[display_columns]
        
    except (json.JSONDecodeError, IOError, KeyError):
        return pd.DataFrame()


def get_history_json():
    if not HISTORY_FILE.exists():
        return "[]"
    
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return f.read()


def get_history_excel():
    df = load_history()
    
    buffer = BytesIO()
    df.to_excel(buffer, index=False, sheet_name="Parking History")
    buffer.seek(0)
    
    return buffer.getvalue()
