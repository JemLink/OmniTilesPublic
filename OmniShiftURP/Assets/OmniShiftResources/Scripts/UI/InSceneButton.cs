using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.SceneManagement;

[System.Serializable]
public class ActivationEvent : UnityEvent { }

public class InSceneButton : MonoBehaviour
{
    public bool activated;

    public enum ActivationType { Hovering, Flash}
    public ActivationType activationType;

    public ActivationEvent OnActivation;

    public ParticleSystem activationParticles;

    [Header("Activation parameter")]
    public float coolDownTime;
    public float timeToHoverOver;
    public float fillSpeed = 1.0f;

    private bool hovering;
    private float timeHoverStart;


    // Start is called before the first frame update
    void Start()
    {
        switch (activationType)
        {
            case ActivationType.Flash:

                GetComponent<Renderer>().material.SetFloat("_Fill", 0.0f);

                break;
            case ActivationType.Hovering:

                GetComponent<Renderer>().material.SetFloat("_Fill", 6.4f);

                break;
            default:
                Debug.LogError("Something went wrong in switch case statement");
                break;
        }
    }

    // Update is called once per frame
    void Update()
    {
        var Ray = new Ray(transform.position, -Vector3.forward);
        RaycastHit hit;

        switch (activationType)
        {
            case ActivationType.Flash:
                
                if (Physics.Raycast(Ray, out hit, LayerMask.NameToLayer("Brush")))
                {
                    if (!activated)
                    {
                        Activate();
                        StartCoroutine(CoolDown(coolDownTime));
                    }
                    
                }

                break;
            case ActivationType.Hovering:
               
                if (Physics.Raycast(Ray, out hit, LayerMask.NameToLayer("Brush")))
                {
                    if (hit.transform.GetComponentInChildren<Brush>().active)
                    {
                        HoverActivation();
                    }
                    else
                    {
                        ResetHovering();
                    }
                }
                else
                {
                    ResetHovering();
                }

                break;
            default:
                Debug.LogError("Something went wrong in switch case statement");
                break;
        }

        
    }

    private void ResetHovering()
    {
        if (hovering)
        {
            Debug.Log("No hovering");
            hovering = false;
            activated = false;
        }

        ChangeFillRate();
    }


    private void HoverActivation()
    {

        if (!hovering)
        {
            Debug.Log("Started Hover");
            hovering = true;
            timeHoverStart = Time.time;
        }
        else
        {

            ChangeFillRate();
            if (Time.time - timeHoverStart > timeToHoverOver)
            {
                timeHoverStart = Time.time;
                GetComponent<Renderer>().material.SetFloat("_Fill", 6.4f);
                Activate();
            }
        }
    }


    public void PlayParticles()
    {
        activationParticles.Play();
    }


    public void LoadSceneByName(string sceneName)
    {
        SceneManager.LoadScene(sceneName, LoadSceneMode.Single);
    }


    public void LoadSceneByID(int sceneID)
    {
        SceneManager.LoadScene(sceneID, LoadSceneMode.Single);
    }


    private void Activate()
    {
        if (!activated)
        {
            activated = true;
            Debug.Log("Activated");
            OnActivation.Invoke();
        }
        
    }

    private void ChangeFillRate()
    {
        Renderer rend = GetComponent<Renderer>();
        float fill = rend.material.GetFloat("_Fill");

        float fillStep =  6.4f / timeToHoverOver * Time.deltaTime;
        
        if (hovering)
        {
            fill -= fillStep;
            // Maximum fill is 2*pi, circle is full at 0 and empty at 6.4
            rend.material.SetFloat("_Fill", Mathf.Clamp(fill, 0.0f, 6.4f));
        }
        else
        {
            rend.material.SetFloat("_Fill", 6.4f);
        }
    }

    IEnumerator CoolDown(float seconds)
    {
        yield return new WaitForSeconds(seconds);
        activated = false;
    }
}
