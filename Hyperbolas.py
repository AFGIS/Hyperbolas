import math

import csv,sys, gc, arcpy, os

csv_file = arcpy.GetParameterAsText(0)


output_path = arcpy.GetParameterAsText(1)
output_filename = arcpy.GetParameterAsText(2)
output = os.path.join(output_path, output_filename + ".shp")
arcpy.AddMessage(output)

save_csv_file = arcpy.GetParameterAsText(3)
temp_filename = os.path.join(output_path, output_filename + ".csv")
arcpy.AddMessage(temp_filename)

spatial_reference = arcpy.GetParameterAsText(4)

trace_threshold = float(arcpy.GetParameterAsText(5))

closest_points = []
subset_trace = []
temp_layer = "Temp"


def find_highest_point(list_of_points):
    highest_point = []
    depth_index = 4
    first_item = True
    for point in list_of_points:
        point[depth_index] = -abs(float(point[depth_index]))
        if first_item:
            largest_depth = point[depth_index]
            first_item = False
        elif point[depth_index] < largest_depth:
            largest_depth = point[depth_index]
            highest_point = point
    return highest_point

def create_file(head, body):
    with open(temp_filename, 'wb') as csvfile_write:
        file_writer = csv.writer(csvfile_write, delimiter=',')
        file_writer.writerow(head)
        file_writer.writerows(body)
    del file_writer


with open(csv_file) as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    rows = []
    for row in csvreader:
        rows.append(row)
    trace_field = 3
    first_row = True
    for item in rows:
        this_trace_number = float(item[trace_field])
        if first_row:
            subset_trace.append(item)
            trace_number = this_trace_number
            first_row = False
        elif (this_trace_number >= (trace_number - trace_threshold)) & \
                (this_trace_number <= (trace_number + trace_threshold)):
            subset_trace.append(item)
            trace_number = float(item[trace_field])
        else:
            closest_points.append(find_highest_point(subset_trace))
            del subset_trace
            subset_trace = [item]
            trace_number = this_trace_number

    else:
        header = ['X', 'Y', 'Line', 'Trace', 'Depth/Time', 'Amplitude']
        create_file(header, closest_points)
        arcpy.management.MakeXYEventLayer(temp_filename, 'X', 'Y', temp_layer, spatial_reference)
        arcpy.CopyFeatures_management(temp_layer, output)

del subset_trace, closest_points, rows, csvreader, csvfile
if not save_csv_file:
    arcpy.Delete_management(temp_filename)
    #os.remove(temp_filename)
gc.collect()

