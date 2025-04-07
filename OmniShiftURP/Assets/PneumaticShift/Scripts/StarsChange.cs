using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class StarsChange : MonoBehaviour
{
    public GameObject starConstellations;
    public GameObject starImages;

    public bool closed;
    public bool overlay;


    private Renderer constRend;
    private Renderer imageRend;

    // Start is called before the first frame update
    void Start()
    {
        constRend = starConstellations.GetComponent<Renderer>();
        imageRend = starImages.GetComponent<Renderer>();

        if (closed)
        {
            SetTransparencyTo(imageRend, 1.0f);
            SetTransparencyTo(constRend, 0.0f);
        }
        else
        {
            SetTransparencyTo(imageRend, 0.0f);
            SetTransparencyTo(constRend, 1.0f);
        }
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void SetTransparencyTo(Renderer rend, float alpha)
    {
        rend.material.color = new Color(rend.material.color.r, rend.material.color.g, rend.material.color.b, alpha);
    }

    public void ToggleOverlay()
    {
        if (!closed)
        {
            overlay = !overlay;

            if (overlay)
            {
                SetTransparencyTo(imageRend, 0.4f);
            }
            else
            {
                SetTransparencyTo(imageRend, 0.0f);
            }
        }
        
    }

    public void SwitchTransparency()
    {
        closed = !closed;

        if (closed)
        {
            SetTransparencyTo(imageRend, 1.0f);
            SetTransparencyTo(constRend, 0.0f);
        }
        else
        {
            SetTransparencyTo(imageRend, 0.0f);
            SetTransparencyTo(constRend, 1.0f);
        }
    }
}
