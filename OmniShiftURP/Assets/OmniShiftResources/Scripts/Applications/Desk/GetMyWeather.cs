/*
 * based but not same to source that was updated to used unity version (2020.3.15) by Jana Hoffard:
 * https://forum.unity.com/threads/current-weather-script.242009/
 * 
 * info about weeather api: https://home.openweathermap.org/
 */

using UnityEngine;
using System.Collections;
using UnityEngine.Networking;
using System.Net;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System;
using SimpleJSON;

public class GetMyWeather : MonoBehaviour
{
    public string API_Key;
    //public UILabel myWeatherLabel;
    public string weatherLabel;
    //public UITexture myWeatherCondition;
    public string weatherCondition;

    public string currentIP;
    public string currentCountry;
    public string currentCity;
    public string latitude;
    public string longitude;

    //retrieved from weather API
    [Header("Weather Info")]
    public string retrievedCountry;
    public string retrievedCity;
    public int conditionID;
    public string conditionName;
    public string conditionImage;
    public string temperature;
    public string feltTemperature;
    public string humidity;
    public Texture2D weatherImage;


    void Start()
    {
        //StartCoroutine(SendRequest());
    }

    IEnumerator SendRequest()
    {
        //get the players IP, City, Country

        currentIP = GetLocalIPAddress();

        var www = new UnityWebRequest("http://www.geoplugin.net/json.gp?ip=" + currentIP.Substring(0, 10))
        {
            downloadHandler = new DownloadHandlerBuffer()
        };

        yield return www.SendWebRequest();

        if (www.result == UnityWebRequest.Result.ConnectionError || www.result == UnityWebRequest.Result.ProtocolError)
        {
            yield break;
        }
        else
        {
            //Debug.Log("Text: " + www.downloadHandler.text);
            var N = JSON.Parse(www.downloadHandler.text);
            currentCity = N["geoplugin_city"].Value;
            currentCountry = N["geoplugin_countryName"].Value;
            latitude = N["geoplugin_latitude"].Value;
            longitude = N["geoplugin_longitude"].Value;

        }

        //get the current weather
        var request = new UnityWebRequest("http://api.openweathermap.org/data/2.5/weather?lat=" + latitude + "&lon=" + longitude + "&appid=" + API_Key)
        {
            downloadHandler = new DownloadHandlerBuffer()
        };
        yield return request.SendWebRequest();
        if (request.result == UnityWebRequest.Result.ConnectionError || request.result == UnityWebRequest.Result.ProtocolError)
        {
            yield break;
        }
        else
        {
            var N = JSON.Parse(request.downloadHandler.text);

            retrievedCountry = N["sys"]["country"].Value; //get the country
            retrievedCity = N["name"].Value; //get the city

            string temp = N["main"]["temp"].Value; //get the temperature
            float tempTemp; //variable to hold the parsed temperature
            float.TryParse(temp, out tempTemp); //parse the temperature
            float finalTemp = Mathf.Round((tempTemp - 273.0f) * 10) / 10; //holds the actual converted temperature

            string feltTemp = N["main"]["feels_like"].Value; //get the temperature
            float feltTempTemp; //variable to hold the parsed temperature
            float.TryParse(feltTemp, out feltTempTemp); //parse the temperature
            float finalFeltTemp = Mathf.Round((feltTempTemp - 273.0f) * 10) / 10; //holds the actual converted temperature

            int.TryParse(N["weather"][0]["id"].Value, out conditionID); //get the current condition ID
            conditionName = N["weather"][0]["main"].Value; //get the current condition Name
            //conditionName = N["weather"][0]["description"].Value; //get the current condition Description
            conditionImage = N["weather"][0]["icon"].Value; //get the current condition Image

            //put all the retrieved stuff in the label
            temperature = "" + finalTemp;
            feltTemperature = "" + finalFeltTemp;
            humidity = N["main"]["humidity"].Value; //get the humidity
            weatherLabel =
                "Country: " + retrievedCountry
                + "\nCity: " + retrievedCity
                + "\nTemperature: " + finalTemp + " C"
                + "\nCurrent Condition: " + conditionName
                + "\nCondition Code: " + conditionID;
        }



        //get our weather image
        WWW conditionRequest = new WWW("http://openweathermap.org/img/w/" + conditionImage + ".png");
        //WWW conditionRequest = new WWW("http://openweathermap.org/img/w/" + "09d.png");
        yield return conditionRequest;
        if (conditionRequest.error == null || conditionRequest.error == "")
        {
            //create the material, put in the downloaded texture and make it visible
            var texture = conditionRequest.texture;
            weatherImage = texture;
        }
        else
        {
            Debug.Log("WWW error: " + conditionRequest.error);
        }
    }

    private string GetLocalIPAddress()
    {
        var host = Dns.GetHostEntry(Dns.GetHostName());
        foreach (var ip in host.AddressList)
        {
            if (ip.AddressFamily == AddressFamily.InterNetwork)
            {
                //Debug.Log("IP: " + ip.ToString());
                return ip.ToString();
            }
        }
        throw new System.Exception("No network adapters with an IPv4 address in the system!");
    }

    public void SendNewRequest()
    {
        StartCoroutine(SendRequest());
    }
}
