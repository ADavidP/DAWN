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

import static android.content.Intent.FLAG_ACTIVITY_SINGLE_TOP;

public class ColourPicker extends AppCompatActivity {

    @ColorInt
    Integer currentColour;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_colour_picker);

        Intent intent = getIntent();
        currentColour = intent.getIntExtra(MainActivity.COLOUR, R.color.warm_glow);

        setSelectedGradient(currentColour);
        setSelectedPalette(currentColour);
        setSliders(currentColour);

        ColorPickerView colourPicker = findViewById(R.id.gradientColourPicker);
        colourPicker.setColorListener(new ColorListener() {
            @Override
            public void onColorSelected(int color, boolean fromUser) {
                currentColour = color;
                setSelectedPalette(currentColour);
                setSliders(currentColour);
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
        ImageView[] colourPalette = {
                findViewById(R.id.red_button),
                findViewById(R.id.orange_button),
                findViewById(R.id.yellow_button),
                findViewById(R.id.default_button),
                findViewById(R.id.green_button),
                findViewById(R.id.blue_button),
                findViewById(R.id.purple_button)
        };

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
        currentColour = R.color.red;
        setSelectedGradient(currentColour);
        setSliders(currentColour);
    }

    public void setOrange(View view){
        currentColour = R.color.orange;
        setSelectedGradient(currentColour);
        setSliders(currentColour);
    }

    public void setYellow(View view){
        currentColour = R.color.yellow;
        setSelectedGradient(currentColour);
        setSliders(currentColour);
    }

    public void setDefault(View view){
        currentColour = R.color.warm_glow;
        setSelectedGradient(currentColour);
        setSliders(currentColour);
    }

    public void setGreen(View view){
        currentColour = R.color.green;
        setSelectedGradient(currentColour);
        setSliders(currentColour);
    }

    public void setBlue(View view){
        currentColour = R.color.blue;
        setSelectedGradient(currentColour);
        setSliders(currentColour);
    }

    public void setPurple(View view){
        currentColour = R.color.purple;
        setSelectedGradient(currentColour);
        setSliders(currentColour);
    }

    public void sliderChange(){
        SeekBar redSlider = findViewById(R.id.red_slider);
        Integer red = redSlider.getProgress();

        SeekBar greenSlider = findViewById(R.id.green_slider);
        Integer green = greenSlider.getProgress();

        SeekBar blueSlider = findViewById(R.id.blue_slider);
        Integer blue = blueSlider.getProgress();

        currentColour = Color.rgb(red, green, blue);
        setSelectedGradient(currentColour);
        setSelectedPalette(currentColour);
    }

    public void colourCancel (View view){
        Intent intent = new Intent(this, ColourPicker.class);
        intent.addFlags (FLAG_ACTIVITY_SINGLE_TOP);
        startActivity(intent);
    }

    public void colourChoice (View view){
        Intent intent = new Intent(this, ColourPicker.class);
        intent.addFlags (FLAG_ACTIVITY_SINGLE_TOP);
        intent.putExtra(MainActivity.COLOUR, currentColour);
        startActivity(intent);
    }

}