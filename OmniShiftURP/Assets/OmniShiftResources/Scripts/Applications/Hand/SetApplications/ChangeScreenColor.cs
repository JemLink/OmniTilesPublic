using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;


public class ChangeScreenColor : WebbedHandApplications
{
    Color screenColor;

    public Volume volume;
    private ColorAdjustments adjustment;

    private int colorActive = 0;

    // Start is called before the first frame update
    void Start()
    {
        if (volume)
        {
            volume.profile.TryGet(out adjustment);
        }

        screenColor = gameObject.GetComponent<Renderer>().material.color;
    }

    // Update is called once per frame
    void Update()
    {
        
    }


    public override void ExecuteApplication(Hand hand)
    {
        if (!active)
        {

            if(colorActive == 0)
            {
                Color lerpedCol = Color.Lerp(Color.white, screenColor, 0.5f);

                adjustment.colorFilter.value = adjustment.colorFilter.value + screenColor * 0.5f;
                
                colorActive = 1;
            }
            else if(colorActive == 1)
            {
                Color lerpedCol = Color.Lerp(Color.white, screenColor, 0.5f);

                adjustment.colorFilter.value = adjustment.colorFilter.value - screenColor * 0.5f;
                
                colorActive = 0;
            }

        }

        active = true;
    }

    public override void StopApplication()
    {
        //if (active)
        //{
        //    adjustment.colorFilter.value = new Color(1.0f, 1.0f, 1.0f, 1.0f);
        //    Debug.Log("Reversed color: " + adjustment.colorFilter.value);
        //}
        
        active = false;

    }
}
