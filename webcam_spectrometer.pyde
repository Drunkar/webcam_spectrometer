# https://github.com/Drunkar/gicentreutils
add_library('gicentreUtils')
add_library('video')

debug_mode = False
c = None
frame = None
x_c = None
y_c = None
x_c_viewport = None
y_c_viewport = None
x_debug_window = None
y_debug_window = None
captured_lines = []
line_chart_i = None
line_chart_r = None
line_chart_g = None
line_chart_b = None
margin_chart = 30
margin_yaxis = 90
captured_max = 50
wavelength_nm_min = 0
wavelength_nm_max = 800
intensity_min = 0
intensity_max = 100
intensities = {"R": [], "G": [], "B": [], "Intensity": []}


def clear_intensities():
    global intensities
    intensities = {"R": [], "G": [], "B": [], "Intensity": []}


def setup():
    global c, frame, x_c, y_c, x_c_viewport, y_c_viewport, line_chart_i, line_chart_r, line_chart_g, line_chart_b
    # fullScreen()
    size(960, 640)
    smooth()
    x_c_viewport = width / 4
    y_c_viewport = height / 4
    x_c = width
    y_c = height

    c = Capture(this, x_c, y_c, 8)  # Captureオブジェクトを生成
    c.start()
    frame = createGraphics(x_c_viewport, y_c_viewport)

    textFont(createFont("Arial", 10), 32)
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


def draw():
    global captured_lines, intensities, x_c_viewport, y_c_viewport
    background(200)
    noStroke()
    fill(color(235, 235, 235, 3))
    for i in range(height / 10):
        ellipse(width / 2, height / 2, height * 2 - 5 * i, height * 2 - 5 * i)

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

    c.loadPixels()
    captured_lines.append(c.pixels[x_c * y_c / 2: x_c * y_c / 2 + x_c])
    if len(captured_lines) > captured_max:
        del captured_lines[0]

    pushMatrix()
    translate(x_debug_window + margin_chart + margin_yaxis, 0)
    scale((width - x_debug_window - margin_chart * 2 - margin_yaxis) / float(x_c), 1)
    for i, captured_line in enumerate(reversed(captured_lines)):
        for j, p in enumerate(captured_line):
            stroke(p)
            point(j, height - captured_max - margin_chart + i)
    popMatrix()

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
    x_data = [(i + 1) * x_interval for i in range(x_c)]
    line_chart_i.setData(x_data, intensities["Intensity"])
    line_chart_r.setData(x_data, intensities["R"])
    line_chart_g.setData(x_data, intensities["G"])
    line_chart_b.setData(x_data, intensities["B"])

    line_chart_i.draw(x_debug_window + margin_chart, margin_chart, width -
                      x_debug_window - margin_chart, height - captured_max - margin_chart * 2.5)
    line_chart_r.draw(x_debug_window + margin_chart, margin_chart, width -
                      x_debug_window - margin_chart, height - captured_max - margin_chart * 2.5)
    line_chart_g.draw(x_debug_window + margin_chart, margin_chart, width -
                      x_debug_window - margin_chart, height - captured_max - margin_chart * 2.5)
    line_chart_b.draw(x_debug_window + margin_chart, margin_chart, width -
                      x_debug_window - margin_chart, height - captured_max - margin_chart * 2.5)


def captureEvent(c):
    """Capture update event."""
    c.read()
    if frame is not None:
        # draw resized image to buffer -> faster than PImage.resize()
        frame.beginDraw()
        frame.image(c, 0, 0, x_c_viewport, y_c_viewport)
        frame.endDraw()


def keyPressed():
    global debug_mode
    if key == "d":
        debug_mode = not debug_mode
