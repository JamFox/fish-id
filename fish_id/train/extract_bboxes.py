
from torch import hub, tensor, device, cuda, unsqueeze
from torchvision.io.video import read_video
from torchvision import set_video_backend, transforms
from nonmaxsupression import non_max_suppression
import numpy as np
from PIL import Image
import os

set_video_backend("pyav")
device = device("cuda" if cuda.is_available() else "cpu")

DEFAULT_IN_DIR = 'intro/videos'
DEFAULT_OUT_DIR = 'bboxes'
DEFAULT_MIN_CONF = 0.9

def export_bboxes(video_path, output_path, model, min_conf, device):
    """Exports png frames from video using bounding box information and prediction confidence.

    Parameters
    ----------
    video_path : str
        Path to video to extract frames from.
    output_path : str
        Path where to extract frames to.
    model : models.common
        The torchvision.models subpackage imported or custom model to use for evaluating frames.
    min_conf : float
        The minimum prediction confidence percentage. Should be a value between 0 and 1.
    device : torch.device
        The device on which a torch.Tensor is or will be allocated (i.e. 'cpu' or 'cuda').
    """
    # Make sure that output path exists
    os.makedirs(output_path, exist_ok=True)
    # Read the video and convert it to a PyTorch tensor
    vid = read_video(video_path)[0].to(device)
    # Get video name without file extension
    base_name = os.path.basename(video_path)
    base_name, ext = os.path.splitext(base_name)
    
    # Loop through each tensor frame in the video
    for i, frame in enumerate(vid):
        # Convert the frame to a PyTorch tensor
        frame = unsqueeze(frame, 0)
        # Resize the frame to 640x640 permuted to n_frames, H, W, C
        frame = transforms.Resize((640, 640))(frame.permute(0,3,1,2))/255
        # Apply non-maximum suppression to get the bounding box predictions
        pred = non_max_suppression(model(frame))
        
        # Loop through each bounding box prediction
        for p in pred:
            # Skip if frame is empty
            if len(p) == 0:
                continue
            # Extract the bounding box coordinates, confidence, and class
            x1, y1, x2, y2, conf, cls = p[0]
            # Skip if confidence is too low
            if conf < min_conf:
                continue
            # Convert the bounding box coordinates from float to integer format
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            # Crop the frame using the bounding box coordinates
            cropped_frame = frame[:, :, y1:y2, x1:x2]
            # Convert the PyTorch tensor to a numpy array
            np_frame = cropped_frame.permute(0,2,3,1).cpu().numpy()[0]
            # Generate full path of image to be saved
            output_full_path = output_path + '/' + f"{base_name}_frame_{i}_bbox_{x1}_{y1}_{x2}_{y2}.png"
            
            # Save image if it does not exist already
            if not os.path.exists(output_full_path):
                try:
                    # Save the numpy array as a PNG image
                    Image.fromarray(np.uint8(np_frame*255)).save(output_full_path)
                # Improperly cropped frames may fail
                # So we catch errors here to skip them
                except Exception as e: print(f"Error extracting frame {i} from {video_path}: {e}")

if __name__ == '__main__':
    # Loading fish detection model from torch hub using custom trained weights
    weights='intro/annotations/models/last.pt'
    model = hub.load('ultralytics/yolov5', 'custom', path=weights,  _verbose=False)
    model = model.to(device)
    model = model.eval() #put model into evaluation / inference mode (not for training)
    # Loop over each directory under specified directory
    for dir_name, sub_dirs, files in os.walk(DEFAULT_IN_DIR):
        # Loop over each file in the directory
        for file_name in files:
            # Generate full path to file
            file_path = dir_name + '/' + file_name
            # Check if the file ends with .avi extension
            if os.path.splitext(file_name)[1] == '.avi':
                # Extract bounding boxes from video
                export_bboxes(file_path, DEFAULT_OUT_DIR + '/' + os.path.basename(dir_name), model, DEFAULT_MIN_CONF, device)
    print("Finished extracting bounding boxes!")