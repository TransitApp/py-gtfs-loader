import gtfs_loader

import shutil

SORTED_IO = False
ITINERARIES = True

# IN_DIR="/Users/gregorypevnev/Desktop/Transit-PyGtfsLoader/data/stm-in-raw"
# OUT_DIR="/Users/gregorypevnev/Desktop/Transit-PyGtfsLoader/data/stm-out-raw"

# def main():
#   gtfs = gtfs_loader.load(IN_DIR, sorted_read=SORTED_IO, itineraries=ITINERARIES)
#   shutil.rmtree(OUT_DIR, ignore_errors=True)
#   gtfs_loader.patch(gtfs, gtfs_in_dir=IN_DIR, gtfs_out_dir=OUT_DIR, 
#             sorted_output=SORTED_IO, itineraries=ITINERARIES, export_compressed=False)

IN_DIR="/Users/gregorypevnev/Desktop/Transit-PyGtfsLoader/data/stm-in-raw"
COMP_DIR1="/Users/gregorypevnev/Desktop/Transit-PyGtfsLoader/data/stm-comp1"
COMP_DIR2="/Users/gregorypevnev/Desktop/Transit-PyGtfsLoader/data/stm-comp2"
OUT_DIR="/Users/gregorypevnev/Desktop/Transit-PyGtfsLoader/data/stm-out-raw"

def main():
  gtfs1 = gtfs_loader.load(IN_DIR, sorted_read=SORTED_IO, itineraries=ITINERARIES)
  shutil.rmtree(COMP_DIR1, ignore_errors=True)
  gtfs_loader.patch(gtfs1, gtfs_in_dir=IN_DIR, gtfs_out_dir=COMP_DIR1, 
            sorted_output=SORTED_IO, itineraries=ITINERARIES, export_compressed=True)
  
  gtfs2 = gtfs_loader.load(COMP_DIR1, sorted_read=SORTED_IO, itineraries=ITINERARIES)
  shutil.rmtree(COMP_DIR2, ignore_errors=True)
  gtfs_loader.patch(gtfs2, gtfs_in_dir=COMP_DIR1, gtfs_out_dir=COMP_DIR2, 
            sorted_output=SORTED_IO, itineraries=ITINERARIES, export_compressed=True)
  
  gtfs3 = gtfs_loader.load(COMP_DIR2, sorted_read=SORTED_IO, itineraries=ITINERARIES)
  shutil.rmtree(OUT_DIR, ignore_errors=True)
  gtfs_loader.patch(gtfs3, gtfs_in_dir=COMP_DIR2, gtfs_out_dir=OUT_DIR, 
            sorted_output=SORTED_IO, itineraries=ITINERARIES, export_compressed=False)

main()
