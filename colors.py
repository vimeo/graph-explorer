# some colors (light and dark version)
# better would be to compute colors, gradients and lighter/darker versions as needed
colors = {
    'blue': ('#5C9DFF', '#0000B2'),
    'yellow': ('#FFFFB2', '#FFFF00'),
    'green': ('#80CC80', '#009900'),
    'brown': ('#694C2E', '#A59482'),
    'red': ('#FF5C33', '#B24024'),
    'purple': ('#FF94FF', '#995999'),
    'turq': ('#75ACAC', '#197575'),
    'orange': ('#FFC266', '#FF9900'),
    'white': '#FFFFFF',
    'black': '#000000'
}


# from http://chase-seibert.github.io/blog/2011/07/29/python-calculate-lighterdarker-rgb-colors.html
# + fix from 2nd comment cause it was a little broken otherwise
def color_variant(hex_color, brightness_offset=1):
    """ takes a color like #87c95f and produces a lighter or darker variant """
    if len(hex_color) != 7:
        raise Exception("Passed %s into color_variant(), needs to be in #87c95f format." % hex_color)
    rgb_hex = [hex_color[x:x + 2] for x in [1, 3, 5]]
    new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]
    new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int]  # make sure new values are between 0 and 255
    # hex() produces "0x88", we want just "88"
    #return "#" + "".join([hex(i)[2:] for i in new_rgb_int])
    return "#%02x%02x%02x" % tuple(new_rgb_int)
