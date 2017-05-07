from __future__ import print_function
# https://github.com/Drunkar/gicentreutils
add_library("gicentreUtils")
add_library("glvideo")

debug_mode = False
axis_check = False
rgb_check = False
c = None
frame = None
x_c = None
y_c = None
x_c_viewport = None
y_c_viewport = None
x_debug_window = None
y_debug_window = None
x_offset_left = None
x_offset_right = None
y_offset_top = None
y_offset_bottom = None
captured_lines = []
line_chart_i = None
line_chart_r = None
line_chart_g = None
line_chart_b = None
margin_chart = 0
margin_chart_left = 49
margin_chart_right = 34
margin_chart_top = 19
margin_chart_bottom = 36
captured_max = 50
wavelength_nm_min = 380
wavelength_nm_max = 750
intensity_min = 0
intensity_max = 100
intensities = {"R": [], "G": [], "B": [], "Intensity": []}
img_spectrum = None
imgpath_spectrum = "spectrum_380_to_750.png"
mask_spectrum = None
txt_big = None
txt_small = None
txt_tiny = None


def clear_intensities():
    global intensities
    intensities = {"R": [], "G": [], "B": [], "Intensity": []}


def setup():
    global c, frame, x_c, y_c, x_c_viewport, y_c_viewport, img_spectrum, mask_spectrum
    size(960, 640, P2D)
    smooth()
    x_c_viewport = width / 4
    y_c_viewport = height / 4
    x_c = width
    y_c = height

    # capture
    devices = GLCapture.list()
    if 0 < len(devices):
        configs = GLCapture.configs(devices[0])
    # c = GLCapture(this, devices[0], x_c, y_c, 8)
    c = GLCapture(this)
    c.play()
    frame = createGraphics(x_c_viewport, y_c_viewport, P2D)

    # charts
    chartsInit()
    img_spectrum = loadImage(imgpath_spectrum)
    mask_spectrum = createGraphics(img_spectrum.width, img_spectrum.height, P2D)


def draw():
    global captured_lines, intensities, x_c_viewport, y_c_viewport, x_debug_window, y_debug_window
    global img_spectrum, mask_spectrum, x_offset_left, x_offset_right, y_offset_top, y_offset_bottom
    drawBackground()
    
    updateCamera()

    if debug_mode:
        x_debug_window = x_c_viewport
        y_debug_window = y_c_viewport

        # captured frame
        if frame is not None:
            image(frame, 0, 0)

        # center line
        stroke(255, 255, 0, 200)
        line(0, y_debug_window / 2, x_debug_window, y_debug_window / 2)

    else:
        x_debug_window = 0
        y_debug_window = 0

    if axis_check:
        x_offset_left = margin_chart_left
        x_offset_right = margin_chart_right
        y_offset_top = margin_chart_top
        y_offset_bottom = margin_chart_bottom
    else:
        x_offset_left = 0
        x_offset_right = 0
        y_offset_top = 0
        y_offset_bottom = 0

    c.loadPixels()
    captured_lines.append(c.pixels[x_c * y_c / 2: x_c * y_c / 2 + x_c])
    if len(captured_lines) > captured_max:
        del captured_lines[0]

    pushMatrix()
    translate(x_debug_window + margin_chart + x_offset_left, 0)
    scale((x_c - x_debug_window - margin_chart * 2 -
           x_offset_left - x_offset_right) / float(x_c), 1)
    for i, captured_line in enumerate(reversed(captured_lines)):
        for j, p in enumerate(captured_line):
            stroke(p)
            point(j, height - captured_max - margin_chart + i)
    popMatrix()

    line_chart_i.showXAxis(axis_check)
    line_chart_r.showXAxis(axis_check)
    line_chart_g.showXAxis(axis_check)
    line_chart_b.showXAxis(axis_check)
    line_chart_i.showYAxis(axis_check)
    line_chart_r.showYAxis(axis_check)
    line_chart_g.showYAxis(axis_check)
    line_chart_b.showYAxis(axis_check)

    # calculate stats
    clear_intensities()
    for i, p in enumerate(captured_lines[-1]):
        r = (p >> 16) & 255
        g = (p >> 8) & 255
        b = p & 255
        intensities["R"].append(100 * r / 255)
        intensities["G"].append(100 * g / 255)
        intensities["B"].append(100 * b / 255)
        intensities["Intensity"].append(100 * (r + g + b) / (3 * 255))

    x_interval = (wavelength_nm_max - wavelength_nm_min) / float(x_c)
    x_data = [wavelength_nm_min + (i + 1) * x_interval for i in range(x_c)]
    line_chart_i.setData(x_data, intensities["Intensity"])
    line_chart_r.setData(x_data, intensities["R"])
    line_chart_g.setData(x_data, intensities["G"])
    line_chart_b.setData(x_data, intensities["B"])

    pushMatrix()
    translate(x_debug_window + margin_chart + x_offset_left, y_offset_top)
    scale((x_c - x_debug_window - margin_chart * 2 -
           x_offset_left - x_offset_right) / float(x_c), (height - captured_max - margin_chart * 2.5 - y_offset_top - y_offset_bottom) / float(y_c - captured_max))
    # spectrum image
    mask_spectrum.beginDraw()
    mask_spectrum.background(0)
    mask_spectrum.fill(255)
    mask_spectrum.noStroke()
    x_map = float(width) / \
        (wavelength_nm_max - wavelength_nm_min)
    y_map = float(height - captured_max - margin_chart * 2.5) / \
        (intensity_max - intensity_min)
    for i, intensity in enumerate(intensities["Intensity"][:-1]):
        mask_spectrum.quad(
            (x_data[i] - wavelength_nm_min) *
            x_map,
            height - captured_max - margin_chart * 2.5 -
            intensities["Intensity"][i] * y_map,
            (x_data[i + 1] - wavelength_nm_min) *
            x_map,
            height - captured_max - margin_chart * 2.5 -
            intensities["Intensity"][i + 1] * y_map,
            (x_data[i + 1] - wavelength_nm_min) *
            x_map,
            height - captured_max - margin_chart * 2.5,
            (x_data[i] - wavelength_nm_min) *
            x_map,
            height - captured_max - margin_chart * 2.5)
    mask_spectrum.endDraw()
    img_spectrum.mask(mask_spectrum)
    image(img_spectrum, 0, 0)

    pushMatrix()
    resetMatrix()
    translate(x_debug_window + margin_chart, 0)
    scale((x_c - x_debug_window - margin_chart * 2) / float(x_c), 1)
    if rgb_check:
        drawCharts()
    popMatrix()

    drawScale()
    popMatrix()


def drawBackground():
    background(200)
    noStroke()
    fill(color(230, 230, 230, 5))
    for i in range(height / 20):
        ellipse(width / 2, height / 2, height *
                1.5 - 10 * i, height * 1.5 - 10 * i)


def updateCamera():
    if c.available():
        c.read()
        if frame is not None:
            # draw resized image to buffer -> faster than PImage.resize()
            frame.beginDraw()
            frame.image(c, 0, 0, x_c_viewport, y_c_viewport)
            frame.endDraw()


def keyPressed():
    global debug_mode, axis_check, rgb_check
    if key == "d":
        debug_mode = not debug_mode
    elif key == "a":
        axis_check = not axis_check
    elif key == "r":
        rgb_check = not rgb_check


def chartsInit():
    global line_chart_i, line_chart_r, line_chart_g, line_chart_b
    global txt_big, txt_small, txt_tiny
    txt_big = loadFont("SquareSansSerif7-32.vlw")
    txt_small = loadFont("NotoSans-18.vlw")
    txt_tiny = loadFont("NotoSans-14.vlw")
    textFont(txt_big)
    line_chart_i = XYChart(this)
    line_chart_r = XYChart(this)
    line_chart_g = XYChart(this)
    line_chart_b = XYChart(this)
    # Axis formatting and labels.
    line_chart_i.showXAxis(True)
    line_chart_i.showYAxis(True)
    line_chart_i.setMinY(intensity_min)
    line_chart_i.setMaxY(intensity_max)
    line_chart_i.setMinX(wavelength_nm_min)
    line_chart_i.setMaxX(wavelength_nm_max)

    line_chart_r.showXAxis(True)
    line_chart_r.showYAxis(True)
    line_chart_r.setMinY(intensity_min)
    line_chart_r.setMaxY(intensity_max)
    line_chart_r.setMinX(wavelength_nm_min)
    line_chart_r.setMaxX(wavelength_nm_max)

    line_chart_g.showXAxis(True)
    line_chart_g.showYAxis(True)
    line_chart_g.setMinY(intensity_min)
    line_chart_g.setMaxY(intensity_max)
    line_chart_g.setMinX(wavelength_nm_min)
    line_chart_g.setMaxX(wavelength_nm_max)

    line_chart_b.showXAxis(True)
    line_chart_b.showYAxis(True)
    line_chart_b.setMinY(intensity_min)
    line_chart_b.setMaxY(intensity_max)
    line_chart_b.setMinX(wavelength_nm_min)
    line_chart_b.setMaxX(wavelength_nm_max)

    line_chart_i.setYFormat("# ")  # nano meter
    line_chart_i.setXFormat("### nm")  # nano meter
    line_chart_i.setXAxisLabel("Wave length")
    line_chart_i.setYAxisLabel("Intensity [%]")

    line_chart_r.setYFormat("# ")  # nano meter
    line_chart_r.setXFormat("### nm")  # nano meter
    line_chart_r.setXAxisLabel("Wave length")
    line_chart_r.setYAxisLabel("Intensity [%]")

    line_chart_g.setYFormat("# ")  # nano meter
    line_chart_g.setXFormat("### nm")  # nano meter
    line_chart_g.setXAxisLabel("Wave length")
    line_chart_g.setYAxisLabel("Intensity [%]")

    line_chart_b.setYFormat("# ")  # nano meter
    line_chart_b.setXFormat("### nm")  # nano meter
    line_chart_b.setXAxisLabel("Wave length")
    line_chart_b.setYAxisLabel("Intensity [%]")

    # Symbol colours
    line_chart_i.setPointSize(0)
    line_chart_i.setLineColour(color(255, 255, 255, 150))
    line_chart_i.setLineWidth(2)

    line_chart_r.setPointSize(0)
    line_chart_r.setLineColour(color(255, 0, 50, 150))
    line_chart_r.setLineWidth(2)

    line_chart_g.setPointSize(0)
    line_chart_g.setLineColour(color(50, 255, 0, 150))
    line_chart_g.setLineWidth(2)

    line_chart_b.setPointSize(0)
    line_chart_b.setLineColour(color(0, 100, 255, 150))
    line_chart_b.setLineWidth(2)


def drawCharts():
    textFont(txt_small)
    line_chart_i.draw(margin_chart, margin_chart, width -
                      margin_chart, height - captured_max - margin_chart * 2.5)
    line_chart_r.draw(margin_chart, margin_chart, width -
                      margin_chart, height - captured_max - margin_chart * 2.5)
    line_chart_g.draw(margin_chart, margin_chart, width -
                      margin_chart, height - captured_max - margin_chart * 2.5)
    line_chart_b.draw(margin_chart, margin_chart, width -
                      margin_chart, height - captured_max - margin_chart * 2.5)


def drawScale():
    x_unit = float(x_c) / (wavelength_nm_max - wavelength_nm_min)
    y_unit = float(y_c - captured_max) / (intensity_max - intensity_min)
    y_padding = captured_max

    x_scale = createGraphics(img_spectrum.width, img_spectrum.height, P2D)
    x_scale.beginDraw()
    x_scale.background(255, 0)
    x_scale.noFill()
    x_scale.stroke(color(225, 225, 225, 100))
    x_scale.strokeWeight(1)
    for i in range(7):
        x_scale.line(x_unit * 50 * i + x_unit * 20, margin_chart,
                     x_unit * 50 * i + x_unit * 20, height - y_padding)
    x_scale.endDraw()
    manualMask(x_scale, mask_spectrum, 180)
    image(x_scale, 0, 0)

    stroke(color(45, 45, 45, 200))
    strokeWeight(1)
    for i in range(1, 6):
        line(0, height - y_padding - y_unit * 20 * i,
             width, height - y_padding - y_unit * 20 * i)

    # number
    textFont(txt_big)
    fill(225, 200)
    text("Wave Length", width - 280, height - y_padding + 20)
    fill(45, 200)
    text("INTENSITY", 55, 20)

    textFont(txt_small)
    fill(225, 200)
    for i in range(4):
        text(str(i * 100 + 400) + " nm", x_unit * 2 * 50 *
             i + x_unit * 20 + 5, height - y_padding - 2)
    textFont(txt_tiny)
    text("380", 5, height - y_padding - 2)
    text("750", width - 30, height - y_padding - 2)

    textFont(txt_small)
    noStroke()
    for i in range(1, 5):
        fill(225, 200)
        rect(0, height - y_padding - y_unit * 20 * i - 2 - 17, 45, 19)
        fill(45, 200)
        text(str(i * 20) + " %", 2, height - y_padding - y_unit * 20 * i - 2)
    textFont(txt_tiny)
    fill(225, 200)
    rect(0, height - y_padding - 35, 40, 19)
    rect(0, height - y_padding - y_unit * 20 * 5 + 1, 45, 19)
    fill(45, 200)
    text("0", 2, height - y_padding - 20)
    text("100 %", 2, height - y_padding - y_unit * 20 * 5 + 16)


def manualMask(pg, mask, alpha):
    """
    You can set total alpha because alpha in pg was reset.
    """
    mask.loadPixels()
    pg.beginDraw()
    pg.loadPixels()
    for i in range(len(pg.pixels)):

        d = pg.pixels[i]

        # mask alpha
        m_a = mask.pixels[i] & 0xFF
        # display alpha
        d_a = (d >> 24) & 0xFF
        # output alpha (do not change alpha if already transparent)
        if d_a == 0:
            o_a = d_a
            pg.pixels[i] = (o_a << 24) | (0x00FFFFFF & d)
        else:
            o_a = m_a
            if o_a == 0xFF:
                o_a = alpha
            pg.pixels[i] = (o_a << 24) | (0x00FFFFFF & d)

    pg.updatePixels()
    pg.endDraw()