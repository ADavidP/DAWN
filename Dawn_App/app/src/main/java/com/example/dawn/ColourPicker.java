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
        currentColour = intent.getIntExtra(MainActivity.COLOUR, getColor(R.color.warm_glow));

        ColorPickerView colourPicker = findViewById(R.id.gradient_colour_picker);
        colourPicker.setColorListener(new ColorListener() {
            @Override
            public void onColorSelected(int color, boolean fromUser) {
                if (fromUser) {
                    currentColour = color;
                    setSelectedPalette(currentColour);
                    setSliders(currentColour);
                }
            }
        });

        SeekBar redSlider = findViewById(R.id.red_slider);
        redSlider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int i, boolean fromUser) {
                if (fromUser) {sliderChange();}
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        SeekBar greenSlider = findViewById(R.id.green_slider);
        greenSlider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int i, boolean fromUser) {
                if (fromUser) {sliderChange();}
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        SeekBar blueSlider = findViewById(R.id.blue_slider);
        blueSlider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int i, boolean fromUser) {
                if (fromUser) {sliderChange();}
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });
    }

    @Override
    protected void onResume() {
        super.onResume();

        setSelectedPalette(currentColour);
        setSliders(currentColour);
        // Setting gradient doesn't work as set to centre by something else after OnResume
        setSelectedGradient(currentColour);
    }

    private void setSelectedGradient(@ColorInt Integer colour){
        ColorPickerView colourPicker = findViewById(R.id.gradient_colour_picker);
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
        if (colour == getColor(R.color.red))
        {
            findViewById(R.id.red_button).setBackground(
                ResourcesCompat.getDrawable(getResources(), R.drawable.border, null));
        }
        else if (colour == getColor(R.color.orange))
        {
            findViewById(R.id.orange_button).setBackground(
                    ResourcesCompat.getDrawable(getResources(), R.drawable.border, null));
        }
        else if (colour == getColor(R.color.yellow))
        {
            findViewById(R.id.yellow_button).setBackground(
                    ResourcesCompat.getDrawable(getResources(), R.drawable.border, null));
        }
        else if (colour == getColor(R.color.warm_glow))
        {
            findViewById(R.id.default_button).setBackground(
                    ResourcesCompat.getDrawable(getResources(), R.drawable.border, null));
        }
        else if (colour == getColor(R.color.green))
        {
            findViewById(R.id.green_button).setBackground(
                    ResourcesCompat.getDrawable(getResources(), R.drawable.border, null));
        }
        else if (colour == getColor(R.color.blue))
        {
            findViewById(R.id.blue_button).setBackground(
                    ResourcesCompat.getDrawable(getResources(), R.drawable.border, null));
        }
        else if (colour == getColor(R.color.purple))
        {
            findViewById(R.id.purple_button).setBackground(
                    ResourcesCompat.getDrawable(getResources(), R.drawable.border, null));
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
        currentColour = getColor(R.color.red);
        setSelectedGradient(currentColour);
        setSliders(currentColour);
        setSelectedPalette(currentColour);
    }

    public void setOrange(View view){
        currentColour = getColor(R.color.orange);
        setSelectedGradient(currentColour);
        setSliders(currentColour);
        setSelectedPalette(currentColour);
    }

    public void setYellow(View view){
        currentColour = getColor(R.color.yellow);
        setSelectedGradient(currentColour);
        setSliders(currentColour);
        setSelectedPalette(currentColour);
    }

    public void setDefault(View view){
        currentColour = getColor(R.color.warm_glow);
        setSelectedGradient(currentColour);
        setSliders(currentColour);
        setSelectedPalette(currentColour);
    }

    public void setGreen(View view){
        currentColour = getColor(R.color.green);
        setSelectedGradient(currentColour);
        setSliders(currentColour);
        setSelectedPalette(currentColour);
    }

    public void setBlue(View view){
        currentColour = getColor(R.color.blue);
        setSelectedGradient(currentColour);
        setSliders(currentColour);
        setSelectedPalette(currentColour);
    }

    public void setPurple(View view){
        currentColour = getColor(R.color.purple);
        setSelectedGradient(currentColour);
        setSliders(currentColour);
        setSelectedPalette(currentColour);
    }

    public void sliderChange(){
        SeekBar redSlider = findViewById(R.id.red_slider);
        int red = redSlider.getProgress();

        SeekBar greenSlider = findViewById(R.id.green_slider);
        int green = greenSlider.getProgress();

        SeekBar blueSlider = findViewById(R.id.blue_slider);
        int blue = blueSlider.getProgress();

        currentColour = Color.rgb(red, green, blue);
        setSelectedGradient(currentColour);
        setSelectedPalette(currentColour);
    }

    public void colourCancel (View view){
        Intent intent = new Intent(this, MainActivity.class);
        intent.addFlags (FLAG_ACTIVITY_SINGLE_TOP);
        startActivity(intent);
        finish();
    }

    public void colourChoice (View view){
        Intent intent = new Intent(this, MainActivity.class);
        intent.addFlags (FLAG_ACTIVITY_SINGLE_TOP);
        intent.putExtra(MainActivity.NEW_COLOUR, currentColour);
        startActivity(intent);
        finish();
    }
}
