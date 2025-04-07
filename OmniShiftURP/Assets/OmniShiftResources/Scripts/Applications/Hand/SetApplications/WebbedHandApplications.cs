using System.Collections;
using System.Collections.Generic;
using UnityEngine;





public abstract class WebbedHandApplications : MonoBehaviour
{
    public bool active;

    public abstract void ExecuteApplication(Hand hand);

    public abstract void StopApplication();
}
