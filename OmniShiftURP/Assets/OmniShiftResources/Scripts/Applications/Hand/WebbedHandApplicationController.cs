using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class WebbedHandApplicationController : MonoBehaviour
{
    public WebbedHandApplications[] applications;
    public bool active;

    private void OnValidate()
    {
        applications = GetComponents<WebbedHandApplications>();
    }

    public void ExecuteApplication(Hand hand)
    {
        for(int i = 0; i < applications.Length; i++)
        {
            applications[i].ExecuteApplication(hand);
        }
    }

    public void StopApplication()
    {
        for (int i = 0; i < applications.Length; i++)
        {
            applications[i].StopApplication();
        }
    }
}
