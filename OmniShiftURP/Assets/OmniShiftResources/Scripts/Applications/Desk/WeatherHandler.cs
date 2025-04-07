using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[RequireComponent(typeof(TextMesh))]
public class WeatherHandler : MonoBehaviour
{
    [Header("Update paramters")]
    public float refreshTimer;
    public GetMyWeather myWeather;

    [Header("Weather parameters")]
    public string description;
    public string temperature;
    public string feltTemperature;
    public string humidity;
    public string city;
    public string country;
    public Texture2D weatherImage;


    [Header("Display Variables")]
    public bool showDescription;
    public bool showTemperature;
    public bool showFeltTemperature;
    public bool showHumidity;
    public bool showWeatherImage;
    public bool showCity;
    public bool showCountry;

    public Renderer weatherImageRenderer;

    private TextMesh textMesh;


    // Start is called before the first frame update
    void Start()
    {
        textMesh = GetComponent<TextMesh>();

        StartCoroutine(UpdateWeather());
    }

    // Update is called once per frame
    void Update()
    {

    }

    private void DisplayWeather()
    {
        string displayText = "";


        if (showCity)
        {
            displayText += city;
            if (showCountry)
            {
                displayText += "\n" + country;
            }
        }

        if (showDescription)
        {
            if (displayText != "")
            {
                displayText += "\n";
            }

            displayText += description;
        }


        if (showTemperature)
        {
            if (displayText != "")
            {
                displayText += "\n";
            }

            displayText += "Temp " + temperature + "C";


            if (showFeltTemperature)
            {
                displayText += "\nFeel: " + feltTemperature + "C";
            }
        }

        if (showHumidity)
        {
            if (displayText != "")
            {
                displayText += "\n";
            }

            displayText += "Humi: " + humidity + "%";
        }




        if (showWeatherImage && weatherImageRenderer)
        {
            weatherImageRenderer.material.SetTexture("_BaseMap", weatherImage);
        }



        textMesh.text = displayText;

    }

    IEnumerator UpdateWeather()
    {
        myWeather.SendNewRequest();

        yield return new WaitForSeconds(2.0f);

        temperature = myWeather.temperature;
        feltTemperature = myWeather.feltTemperature;
        humidity = myWeather.humidity;
        weatherImage = myWeather.weatherImage;
        city = myWeather.currentCity;
        country = myWeather.currentCountry;
        description = myWeather.conditionName;

        DisplayWeather();
    }
}
