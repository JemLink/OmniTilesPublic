using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;

public class Clock : MonoBehaviour
{
    [Header("DisplayType")]
    public bool all;
    public bool date;
    public bool day;
    public bool time;

    TextMesh textMesh;
    string text;

    private void OnValidate()
    {
        if (all)
        {
            date = true;
            day = true;
            time = true;
        }
    }

    // Start is called before the first frame update
    void Start()
    {
        textMesh = GetComponent<TextMesh>();
        text = textMesh.text;
    }

    // Update is called once per frame
    void Update()
    {
        string displayText = "";
        DateTime dateTime = DateTime.Now;

        if (this.date)
        {
            displayText += dateTime.ToShortDateString();
        }

        if (this.day)
        {
            if(displayText != "")
            {
                displayText += "\n";
            }
            displayText += dateTime.DayOfWeek.ToString();
        }

        if (this.time)
        {
            if (displayText != "")
            {
                displayText += "\n";
            }
            displayText += dateTime.ToShortTimeString();
        }

        textMesh.text = displayText;
    }
}
