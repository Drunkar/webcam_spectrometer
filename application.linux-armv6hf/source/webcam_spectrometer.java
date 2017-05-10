import processing.core.*; 
import processing.data.*; 
import processing.event.*; 
import processing.opengl.*; 

import gohai.glvideo.*; 
import org.gicentre.utils.stat.*; 

import java.util.HashMap; 
import java.util.ArrayList; 
import java.io.File; 
import java.io.BufferedReader; 
import java.io.PrintWriter; 
import java.io.InputStream; 
import java.io.OutputStream; 
import java.io.IOException; 

public class webcam_spectrometer extends PApplet {



// https://github.com/Drunkar/gicentreutils

boolean debug_mode = false;
boolean axis_check = false;
boolean rgb_check = false;
GLCapture c;
PGraphics frame;
int x_c;
int y_c;
int x_c_viewport;
int y_c_viewport;
int x_debug_window;
int y_debug_window;
int x_offset_left;
int x_offset_right;
int y_offset_top;
int y_offset_bottom;
int[][] captured_lines;
int captured_index;
int captured_max = 5;
XYChart line_chart_i;
XYChart line_chart_r;
XYChart line_chart_g;
XYChart line_chart_b;
int margin_chart = 0;
int margin_chart_left = 49;
int margin_chart_right = 34;
int margin_chart_top = 19;
int margin_chart_bottom = 36;
int wavelength_nm_min = 380;
int wavelength_nm_max = 750;
int intensity_min = 0;
int intensity_max = 100;
float[][] intensities;
PImage img_spectrum;
String imgpath_spectrum = "spectrum_380_to_750.png";
PGraphics mask_spectrum;
PFont txt_big;
PFont txt_small;
PFont txt_tiny;


public void clear_intensities() {
  intensities = new float[4][width]; // r, g, b, intensity
}


public void setup() {
  //size(640, 480, P2D);
  
  
  x_c_viewport = width / 4;
  y_c_viewport = height / 4;
  x_c = width;
  y_c = height;
  captured_index = 0;
  clear_intensities();
  captured_lines = new int[captured_max][x_c];

  // capture
  String[] devices = GLCapture.list();
  println("Devices:");
  printArray(devices);
  if (0 < devices.length) {
    String[] configs = GLCapture.configs(devices[0]);
    println("Configs:");
    printArray(configs);
  }
  //c = new GLCapture(this, devices[0], x_c, y_c, 8);
  c = new GLCapture(this);
  c.play();
  frame = createGraphics(x_c_viewport, y_c_viewport, P2D);

  // charts
  chartsInit();
  img_spectrum = loadImage(imgpath_spectrum);
  mask_spectrum = createGraphics(img_spectrum.width, img_spectrum.height, P2D);
}


public void draw() {
  drawBackground();

  updateCamera();

  if (debug_mode) {
    x_debug_window = x_c_viewport;
    y_debug_window = y_c_viewport;

    // captured frame
    if (frame != null) {
      image(frame, 0, 0);
    }

    // center line
    stroke(255, 255, 0, 200);
    line(0, y_debug_window / 2, x_debug_window, y_debug_window / 2);

  } else {
    x_debug_window = 0;
    y_debug_window = 0;
  }

  if (axis_check) {
    x_offset_left = margin_chart_left;
    x_offset_right = margin_chart_right;
    y_offset_top = margin_chart_top;
    y_offset_bottom = margin_chart_bottom;
  } else {
    x_offset_left = 0;
    x_offset_right = 0;
    y_offset_top = 0;
    y_offset_bottom = 0;
  }

  c.loadPixels();
  if (captured_index == captured_max - 1) {
    for(int i=0; i<captured_lines.length - 1; i++) {
      captured_lines[i] = captured_lines[i + 1];
    }
  }
  if (c.pixels.length > 0) {
    captured_lines[captured_index] = subset(c.pixels, x_c * y_c / 2, x_c);

    if (captured_index < captured_max - 1) {
      captured_index++;
    }
  }

  pushMatrix();
  translate(x_debug_window + margin_chart + x_offset_left, 0);
  scale((x_c - x_debug_window - margin_chart * 2 -
       x_offset_left - x_offset_right) / PApplet.parseFloat(x_c), 1);
  for(int i=0; i<captured_lines.length; i++) {
    for(int j=0; j<captured_lines[captured_lines.length -1 - i].length; j++) {
      stroke(captured_lines[captured_lines.length -1 - i][j]);
      point(j, height - captured_max - margin_chart + i);
    }
  }
  popMatrix();

  line_chart_i.showXAxis(axis_check);
  line_chart_r.showXAxis(axis_check);
  line_chart_g.showXAxis(axis_check);
  line_chart_b.showXAxis(axis_check);
  line_chart_i.showYAxis(axis_check);
  line_chart_r.showYAxis(axis_check);
  line_chart_g.showYAxis(axis_check);
  line_chart_b.showYAxis(axis_check);

  // calculate stats
  clear_intensities();
  for(int i=0; i<captured_lines[captured_lines.length - 1].length; i++) {
    int p = captured_lines[captured_lines.length - 1][i];
    int r = (p >> 16) & 255;
    int g = (p >> 8) & 255;
    int b = p & 255;
    intensities[0][i] = 100 * r / 255;
    intensities[1][i] = 100 * g / 255;
    intensities[2][i] = 100 * b / 255;
    intensities[3][i] = 100 * (r + g + b) / (3 * 255);
  }

  float x_interval = (wavelength_nm_max - wavelength_nm_min) / PApplet.parseFloat(x_c);
  float[] x_data = new float[x_c];
  for (int i=0; i<x_c; i++) {
    x_data[i] = wavelength_nm_min + (i + 1) * x_interval;
  }
  line_chart_i.setData(x_data, intensities[3]);
  line_chart_r.setData(x_data, intensities[0]);
  line_chart_g.setData(x_data, intensities[1]);
  line_chart_b.setData(x_data, intensities[2]);

  pushMatrix();
  translate(x_debug_window + margin_chart + x_offset_left, y_offset_top);
  scale((x_c - x_debug_window - margin_chart * 2 -
       x_offset_left - x_offset_right) / PApplet.parseFloat(x_c), (height - captured_max - margin_chart * 2.5f - y_offset_top - y_offset_bottom) / PApplet.parseFloat(y_c - captured_max));
  // spectrum image
  mask_spectrum.beginDraw();
  mask_spectrum.background(0);
  mask_spectrum.fill(255);
  mask_spectrum.noStroke();
  float x_map = PApplet.parseFloat(width) /
    (wavelength_nm_max - wavelength_nm_min);
  float y_map = (height - captured_max - margin_chart * 2.5f) /
    (intensity_max - intensity_min);
  for(int i=0; i<intensities[3].length-1; i++) {
    mask_spectrum.quad(
      (x_data[i] - wavelength_nm_min) *
      x_map,
      height - captured_max - margin_chart * 2.5f -
      intensities[3][i] * y_map,
      (x_data[i + 1] - wavelength_nm_min) *
      x_map,
      height - captured_max - margin_chart * 2.5f -
      intensities[3][i + 1] * y_map,
      (x_data[i + 1] - wavelength_nm_min) *
      x_map,
      height - captured_max - margin_chart * 2.5f,
      (x_data[i] - wavelength_nm_min) *
      x_map,
      height - captured_max - margin_chart * 2.5f);
  }
  mask_spectrum.endDraw();
  img_spectrum.mask(mask_spectrum);
  image(img_spectrum, 0, 0);

  pushMatrix();
  resetMatrix();
  translate(x_debug_window + margin_chart, 0);
  scale((x_c - x_debug_window - margin_chart * 2) / PApplet.parseFloat(x_c), 1);
  if (rgb_check) {
    drawCharts();
  }
  popMatrix();

  drawScale();
  popMatrix();
}


public void drawBackground() {
  background(200);
  noStroke();
  fill(color(230, 230, 230, 5));
  for(int i=0; i<height / 20; i++) {
    ellipse(width / 2, height / 2, height *
        1.5f - 10 * i, height * 1.5f - 10 * i);
  }
}


public void updateCamera() {
  if (c.available()) {
    c.read();
    if (frame != null) {
      // draw resized image to buffer -> faster than PImage.resize()
      frame.beginDraw();
      frame.image(c, 0, 0, x_c_viewport, y_c_viewport);
      frame.endDraw();
    }
  }
}


public void keyPressed() {
  if (key == 'd') {
    debug_mode = !debug_mode;
  } else if (key == 'a') {
    axis_check = !axis_check;
  } else if (key == 'r') {
    rgb_check = !rgb_check;
  }
}


public void chartsInit() {
  txt_big = loadFont("SquareSansSerif7-32.vlw");
  txt_small = loadFont("NotoSans-18.vlw");
  txt_tiny = loadFont("NotoSans-14.vlw");
  textFont(txt_big);
  line_chart_i = new XYChart(this);
  line_chart_r = new XYChart(this);
  line_chart_g = new XYChart(this);
  line_chart_b = new XYChart(this);
  // Axis formatting and labels.
  line_chart_i.showXAxis(true);
  line_chart_i.showYAxis(true);
  line_chart_i.setMinY(intensity_min);
  line_chart_i.setMaxY(intensity_max);
  line_chart_i.setMinX(wavelength_nm_min);
  line_chart_i.setMaxX(wavelength_nm_max);

  line_chart_r.showXAxis(true);
  line_chart_r.showYAxis(true);
  line_chart_r.setMinY(intensity_min);
  line_chart_r.setMaxY(intensity_max);
  line_chart_r.setMinX(wavelength_nm_min);
  line_chart_r.setMaxX(wavelength_nm_max);

  line_chart_g.showXAxis(true);
  line_chart_g.showYAxis(true);
  line_chart_g.setMinY(intensity_min);
  line_chart_g.setMaxY(intensity_max);
  line_chart_g.setMinX(wavelength_nm_min);
  line_chart_g.setMaxX(wavelength_nm_max);

  line_chart_b.showXAxis(true);
  line_chart_b.showYAxis(true);
  line_chart_b.setMinY(intensity_min);
  line_chart_b.setMaxY(intensity_max);
  line_chart_b.setMinX(wavelength_nm_min);
  line_chart_b.setMaxX(wavelength_nm_max);

  line_chart_i.setYFormat("# ");  // nano meter
  line_chart_i.setXFormat("### nm");  // nano meter
  line_chart_i.setXAxisLabel("Wave length");
  line_chart_i.setYAxisLabel("Intensity [%]");

  line_chart_r.setYFormat("# ");  // nano meter
  line_chart_r.setXFormat("### nm");  // nano meter
  line_chart_r.setXAxisLabel("Wave length");
  line_chart_r.setYAxisLabel("Intensity [%]");

  line_chart_g.setYFormat("# ");  // nano meter
  line_chart_g.setXFormat("### nm");  // nano meter
  line_chart_g.setXAxisLabel("Wave length");
  line_chart_g.setYAxisLabel("Intensity [%]");

  line_chart_b.setYFormat("# ");  // nano meter
  line_chart_b.setXFormat("### nm");  // nano meter
  line_chart_b.setXAxisLabel("Wave length");
  line_chart_b.setYAxisLabel("Intensity [%]");

  // Symbol colours
  line_chart_i.setPointSize(0);
  line_chart_i.setLineColour(color(255, 255, 255, 150));
  line_chart_i.setLineWidth(2);

  line_chart_r.setPointSize(0);
  line_chart_r.setLineColour(color(255, 0, 50, 150));
  line_chart_r.setLineWidth(2);

  line_chart_g.setPointSize(0);
  line_chart_g.setLineColour(color(50, 255, 0, 150));
  line_chart_g.setLineWidth(2);

  line_chart_b.setPointSize(0);
  line_chart_b.setLineColour(color(0, 100, 255, 150));
  line_chart_b.setLineWidth(2);
}


public void drawCharts() {
  textFont(txt_small);
  line_chart_i.draw(margin_chart, margin_chart, width -
            margin_chart, height - captured_max - margin_chart * 2.5f);
  line_chart_r.draw(margin_chart, margin_chart, width -
            margin_chart, height - captured_max - margin_chart * 2.5f);
  line_chart_g.draw(margin_chart, margin_chart, width -
            margin_chart, height - captured_max - margin_chart * 2.5f);
  line_chart_b.draw(margin_chart, margin_chart, width -
            margin_chart, height - captured_max - margin_chart * 2.5f);
}


public void drawScale() {
  float x_unit = PApplet.parseFloat(x_c) / (wavelength_nm_max - wavelength_nm_min);
  float y_unit = PApplet.parseFloat(y_c - captured_max) / (intensity_max - intensity_min);
  float y_padding = captured_max;

  stroke(color(225, 225, 225, 100));
  strokeWeight(1);
  for(int i=0; i<7; i++) {
    line(x_unit * 50 * i + x_unit * 20, margin_chart,
         x_unit * 50 * i + x_unit * 20, height - y_padding);
  }

  stroke(color(45, 45, 45, 200));
  strokeWeight(1);
  for(int i=1; i<6; i++) {
    line(0, height - y_padding - y_unit * 20 * i,
       width, height - y_padding - y_unit * 20 * i);
  }

  // number
  textFont(txt_big);
  fill(225, 200);
  text("Wave Length", width - 280, height - y_padding - 20);
  fill(225, 200);
  text("INTENSITY", 55, 20);

  textFont(txt_small);
  fill(225, 200);
  for(int i=0; i<4; i++) {
    text(str(i * 100 + 400) + " nm", x_unit * 2 * 50 *
       i + x_unit * 20 + 5, height - y_padding - 2);
  }
  textFont(txt_tiny);
  text("380", 5, height - y_padding - 2);
  text("750", width - 30, height - y_padding - 2);

  textFont(txt_small);
  noStroke();
  for(int i=1; i<5; i++) {
    fill(225, 200);
    rect(0, height - y_padding - y_unit * 20 * i - 2 - 17, 45, 19);
    fill(45, 200);
    text(str(i * 20) + " %", 2, height - y_padding - y_unit * 20 * i - 2);
  }
  textFont(txt_tiny);
  fill(225, 200);
  rect(0, height - y_padding - 35, 40, 19);
  rect(0, height - y_padding - y_unit * 20 * 5 + 1, 45, 19);
  fill(45, 200);
  text("0", 2, height - y_padding - 20);
  text("100 %", 2, height - y_padding - y_unit * 20 * 5 + 16);
}


public void manualMask(PGraphics pg, PGraphics mask, int alpha) {
  /*
  You can set total alpha because alpha in pg was reset.
  */
  mask.loadPixels();
  pg.beginDraw();
  pg.loadPixels();
  for(int i=0; i<pg.pixels.length; i++) {

    int d = pg.pixels[i];

    // mask alpha
    int m_a = mask.pixels[i] & 0xFF;
    // display alpha
    int d_a = (d >> 24) & 0xFF;
    // output alpha (do not change alpha if already transparent)
    int o_a;
    if(d_a == 0) {
      o_a = d_a;
      pg.pixels[i] = (o_a << 24) | (0x00FFFFFF & d);
    } else {
      o_a = m_a;
      if( o_a == 0xFF) {
        o_a = alpha;
      }
      pg.pixels[i] = (o_a << 24) | (0x00FFFFFF & d);
    }
  }

  pg.updatePixels();
  pg.endDraw();
}
  public void settings() {  fullScreen(P2D);  smooth(); }
  static public void main(String[] passedArgs) {
    String[] appletArgs = new String[] { "webcam_spectrometer" };
    if (passedArgs != null) {
      PApplet.main(concat(appletArgs, passedArgs));
    } else {
      PApplet.main(appletArgs);
    }
  }
}
