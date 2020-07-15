
def insert_img(self, 
                    to_sect: List[str],
                    fg_img_obj: Image,
                    fg_img_path: str,
                    fg_img_size: Tuple[int, int],
                    fg_img_coord: Tuple[int, int]
                    ):
        #TODO Find elegant way to implement boudnary checking for insertion only
        #     consider putting insert_img in shell_assets before transforming dims?
        #TODO Finish
        sections = [s.lower() for s in to_sect]
        fg_img = fg_img_obj
        for sect_i, sect in enumerate(self):
            if to_sect == [] or sect.title in to_sect:
                for img in step.assets.glob("*.png"):
                    curr_img = fg_img.copy()
                    asset = Image.open(img)
                    asset_resize = asset.resize(fg_img_size, Image.ANTIALIAS)
                    curr_img.paste(asset_resize, fg_img_coord, asset_resize.convert('RGBA'))
