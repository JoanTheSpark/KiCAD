# script to create copper leafes for pads
# the output of this script needs to be manually copied&pasted into a kicad_mod file to work
# GPLv3+, JoanTheSpark (2016), written in python 2.7

import sys, os
import shutil
import math

LIST_pts = ["  (fp_poly (pts ",") (layer ",".Cu) (width 0.01))","(xy ",") "]

def FNC_poly (cntr, # (x,y)
              radius,
              sides,
              startangle,
              angle,
              layer,
              ):

    STR_data = ""
    baseX = cntr[0]
    baseY = cntr[1]
    sideangle = angle / sides
    CNT_sides = 0
    STR_1stcoords = ""

    for i in range(sides + 1):
        CNT_sides += 1
        STR_coords = ""
        # calculate the coordinates for the polygon
        pointX = baseX + radius * math.sin(math.radians(sideangle*(i) + startangle))
        pointY = baseY + radius * math.cos(math.radians(sideangle*(i) + startangle))
        # assemble the string for the kicad_mod file
        STR_coords += "{0:.4f}".format(pointX) + " " + "{0:.4f}".format(pointY)
        STR_data += LIST_pts[3] + STR_coords + LIST_pts[4]
        if CNT_sides == 1: # keep 1st point for closing the polygon
            STR_1stcoords = STR_data
        if CNT_sides % 4 is 0: # 4 points (x,y) per line max
            if i < CNT_sides:
                STR_data += "\n    "
    # give back completed string
    return LIST_pts[0] + STR_data + STR_1stcoords + LIST_pts[1] + layer + LIST_pts[2]


if __name__ == '__main__':
    # 4 leafes at top and bottom
    Center = [[-1.2,0.0],[0.0,1.2],[1.2,0.0],[0.0,-1.2]] # x/y coordinates of the centre of 4 circles/arcs/polygons
    StartAngle = [0.0,90.0,180.0,270.0] # in degrees, needs to match number of Center coordinates for correct orientation
    Radius = 0.75 # mm
    Sides = 9
    Angle = 180.0 # degrees
    Layer = ["F","B"]
    
    # now iterate over the leafes positions and layers
    for i in range(len(Layer)):
        for j in range(len(Center)):
            print FNC_poly (Center[j],
                            Radius,
                            Sides,
                            StartAngle[j],
                            Angle,
                            Layer[i],
                            )
