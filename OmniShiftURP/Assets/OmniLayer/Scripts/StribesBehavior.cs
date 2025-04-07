using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class StribesBehavior : MonoBehaviour
{
    // create later instances from this and adapt stribe thickness and number of materials
    public Material mainMat;

    [Header("Objects and their Materials")]
    // we start with 2 materials for now??
    public GameObject front;
    public GameObject back;

    public Material frontMat;
    public Material backMat;


    [Header("Step Settings")]
    public Slider stepSlider;
    public Slider rotationSlider;
    public int steps;

    [Header("Visibility")]
    public Toggle frontVisibleToggle;
    public Toggle backVisibleToggle;



    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        
    }


    public void UpdateSteps()
    {
        steps = (int)stepSlider.value;

        front.GetComponent<Renderer>().material.SetFloat("_Steps", steps);
        back.GetComponent<Renderer>().material.SetFloat("_Steps", steps);
    }

    public void UpdateRotation()
    {
        front.GetComponent<Renderer>().material.SetFloat("_Rotation", rotationSlider.value);
        back.GetComponent<Renderer>().material.SetFloat("_Rotation", rotationSlider.value + 0.5f);
    }

    public void ToggleFrontVisibilty()
    {
        front.GetComponent<Renderer>().enabled = frontVisibleToggle.isOn;
    }

    public void ToggleBackVisibilty()
    {
        back.GetComponent<Renderer>().enabled = backVisibleToggle.isOn;
    }
}
