import strawberry
from datetime import datetime
from bson import ObjectId
import random
from ..db import resources, counters  # Updated import
from ..models.observation import Observation
from ..constants.vital_signs import VITAL_CODES, VALUE_RANGES

# Rest of the file remains the same 