# An assembler for aether9
sdoc = params["INPUT"]
tdoc = params["OUTPUT"]
sinfo = pdf_info.extract(sdoc)
bbox = sinfo["page_size"][0][1]
pcount = sinfo["page_count"]
swidth = bbox["width"]
twidth =  2 * swidth
height = bbox["height"]

imposition_plan = []

for i in range(0,pcount,2):
	imposition_plan.append({
		"target_document" : tdoc,
		"target_page_width" : twidth,
		"target_page_height" : height,
		"pages" : [
			{
			"source_document" : sdoc,
			"source_page" : i,
			"crop_box" : {"left":0,"bottom":0,"width":swidth, "height":height},
			"translate" : [0,0],
			"rotate" : 0,
			"scale" : [1,1]
			},
			{
			"source_document" : sdoc,
			"source_page" : i + 1,
			"crop_box" : {"left":0,"bottom":0,"width":swidth, "height":height},
			"translate" : [swidth,0],
			"rotate" : 0,
			"scale" : [1,1]
			}
			]
	})
	
