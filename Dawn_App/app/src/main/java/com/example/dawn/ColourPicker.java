package com.example.dawn;

import androidx.annotation.ColorInt;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.res.ResourcesCompat;

import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageView;
import android.widget.SeekBar;

import com.skydoves.colorpickerview.ColorPickerView;
import com.skydoves.colorpickerview.listeners.ColorListener;

public class ColourPicker extends AppCompatActivity {

    @ColorInt
    Integer initialColour;
    @ColorInt
    Integer newColour;

    ImageView[] colourPalette = {
            findViewById(R.id.red_button),
            findViewById(R.id.orange_button),
            findViewById(R.id.yellow_button),
            findViewById(R.id.default_button),
            findViewById(R.id.green_button),
            findViewById(R.id.blue_button),
            findViewById(R.id.purple_button)
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_colour_picker);

        Intent intent = getIntent();
        initialColour = intent.getIntExtra(MainActivity.COLOUR, R.color.warm_glow);
        newColour = initialColour;

        setSelectedGradient(newColour);
        setSelectedPalette(newColour);
        setSliders(newColour);

        ColorPickerView colourPicker = findViewById(R.id.gradientColourPicker);
        colourPicker.setColorListener(new ColorListener() {
            @Override
            public void onColorSelected(int color, boolean fromUser) {
                newColour = color;
                setSelectedPalette(newColour);
                setSliders(newColour);
            }
        });

        SeekBar redSlider = findViewById(R.id.red_slider);
        redSlider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int i, boolean b) {
                if (b) {sliderChange();};
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        SeekBar greenSlider = findViewById(R.id.green_slider);
        greenSlider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int i, boolean b) {
                if (b) {sliderChange();};
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        SeekBar blueSlider = findViewById(R.id.blue_slider);
        blueSlider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int i, boolean b) {
                if (b) {sliderChange();};
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });
    }

    private void setSelectedGradient(@ColorInt Integer colour){
        ColorPickerView colourPicker = findViewById(R.id.gradientColourPicker);
        try {
            colourPicker.selectByHsvColor(colour);
        }
        // Exception only thrown if drawable which isn't the default colour wheel is used
        catch (IllegalAccessException ignored) {}

    }

    private void setSelectedPalette(@ColorInt Integer colour){
        for (ImageView imageView : colourPalette) {
            imageView.setBackground(null);
        }
        switch (colour){
            case R.color.red:
                findViewById(R.id.red_button).setBackground(
                        ResourcesCompat.getDrawable(getResources(), R.drawable.border, null));
                break;
            case R.color.orange:
                findViewById(R.id.orange_button).setBackground(
                        ResourcesCompat.getDrawable(getResources(), R.drawable.border, null));
                break;
            case R.color.yellow:
                findViewById(R.id.yellow_button).setBackground(
                        ResourcesCompat.getDrawable(getResources(), R.drawable.border, null));
                break;
            case R.color.warm_glow:
                findViewById(R.id.default_button).setBackground(
                        ResourcesCompat.getDrawable(getResources(), R.drawable.border, null));
                break;
            case R.color.green:
                findViewById(R.id.green_button).setBackground(
                        ResourcesCompat.getDrawable(getResources(), R.drawable.border, null));
                break;
            case R.color.blue:
                findViewById(R.id.blue_button).setBackground(
                        ResourcesCompat.getDrawable(getResources(), R.drawable.border, null));
                break;
            case R.color.purple:
                findViewById(R.id.purple_button).setBackground(
                        ResourcesCompat.getDrawable(getResources(), R.drawable.border, null));
                break;
        }
    }

    private void setSliders(@ColorInt Integer colour){
        SeekBar redSlider = findViewById(R.id.red_slider);
        redSlider.setMax(255);
        redSlider.setProgress(Color.red(colour));

        SeekBar greenSlider = findViewById(R.id.green_slider);
        greenSlider.setMax(255);
        greenSlider.setProgress(Color.green(colour));

        SeekBar blueSlider = findViewById(R.id.blue_slider);
        blueSlider.setMax(255);
        blueSlider.setProgress(Color.blue(colour));
    }

    public void setRed(View view) {
        newColour = R.color.red;
        setSelectedGradient(newColour);
        setSliders(newColour);
    }

    public void setOrange(View view){
        newColour = R.color.orange;
        setSelectedGradient(newColour);
        setSliders(newColour);
    }

    public void setYellow(View view){
        newColour = R.color.yellow;
        setSelectedGradient(newColour);
        setSliders(newColour);
    }

    public void setDefault(View view){
        newColour = R.color.warm_glow;
        setSelectedGradient(newColour);
        setSliders(newColour);
    }

    public void setGreen(View view){
        newColour = R.color.green;
        setSelectedGradient(newColour);
        setSliders(newColour);
    }

    public void setBlue(View view){
        newColour = R.color.blue;
        setSelectedGradient(newColour);
        setSliders(newColour);
    }

    public void setPurple(View view){
        newColour = R.color.purple;
        setSelectedGradient(newColour);
        setSliders(newColour);
    }

    public void sliderChange(){
        SeekBar redSlider = findViewById(R.id.red_slider);
        Integer red = redSlider.getProgress();

        SeekBar greenSlider = findViewById(R.id.green_slider);
        Integer green = greenSlider.getProgress();

        SeekBar blueSlider = findViewById(R.id.blue_slider);
        Integer blue = blueSlider.getProgress();

        newColour = Color.rgb(red, green, blue);
        setSelectedGradient(newColour);
        setSelectedPalette(newColour);
    }

}