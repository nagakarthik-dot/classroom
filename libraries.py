import re
import pandas as pd
import numpy as np
import datetime
import os
import numpy as np
import time
import json
import http
import requests
import math
from datetime import datetime as dt
import logging
import sys
import gurobipy as gp
from gurobipy import GRB

logging.basicConfig(filename="Scenerio.log",filemode="w",level=logging.INFO, format='%(levelname)s %(asctime)s : %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')