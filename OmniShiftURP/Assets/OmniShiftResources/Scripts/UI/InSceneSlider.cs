using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

[Serializable]
public class SliderMovementEvent : UnityEvent<float> { }

public class InSceneSlider : MonoBehaviour
{
    

    [Header("Slider Values")]
    public float min;
    public float max;
    public float value;

    [Header("Behaviour")]
    public SliderMovementEvent OnSliderMove;

    [Header("Slider Movement")]
    public Transform minPosition;
    public Transform maxPosition;
    public GameObject handle;


    // Start is called before the first frame update
    void Start()
    {
        
    }

    private void OnValidate()
    {
        UpdatePosition(value);
    }

    // Update is called once per frame
    void Update()
    {
        var Ray = new Ray(handle.transform.position, -Vector3.forward);
        RaycastHit hit;

        for(int i = 0; i < 20; i++)
        {
            float x = UnityEngine.Random.Range(-0.5f, 0.5f) * handle.transform.lossyScale.x;
            float y = UnityEngine.Random.Range(-0.5f, 0.5f) * handle.transform.lossyScale.y;

            Vector3 origin = new Vector3(handle.transform.position.x + x, handle.transform.position.y + y, handle.transform.position.z);
            Debug.DrawLine(handle.transform.position, origin, Color.cyan);
            Ray = new Ray(origin, -Vector3.forward);
            if (Physics.Raycast(Ray, out hit, LayerMask.NameToLayer("Brush")))
            {
                if (hit.transform.GetComponentInChildren<Brush>().active)
                {
                    MoveSlider(hit.transform.position);
                }
                break;
            }
        }

        
    }


    // Movement
    public void MoveSlider(Vector3 newPos)
    {
        if(!(newPos == handle.transform.position))
        {
            Vector3 lhs = (newPos - minPosition.position);
            Vector3 rhs = (maxPosition.position - minPosition.position);

            //get projection of brush onto slider
            newPos = minPosition.position + Vector3.Project(lhs, rhs);


            // make sure that handle will not go over min and max pos
            Vector3 direction = (newPos - minPosition.position).normalized;
            if (Vector3.Dot(direction, (maxPosition.position - minPosition.position).normalized) <= 0)
            {
                newPos = minPosition.position;
            }
            direction = (newPos - maxPosition.position).normalized;
            if (Vector3.Dot(direction, (minPosition.position - maxPosition.position).normalized) <= 0)
            {
                newPos = maxPosition.position;
            }

            // update position of handle
            handle.transform.position = newPos;// minPosition.position + newPos;
            UpdateValue(handle.transform.position);

            OnSliderMove.Invoke(value);
        }
        
    }



    // Value updates


    private void UpdatePosition(float value)
    {
        if(value < min)
        {
            value = min;
        }

        if(value > max)
        {
            value = max;
        }

        this.value = value;
        Vector3 newPos = (maxPosition.position - minPosition.position) * Map(value);
        handle.transform.position = minPosition.position + newPos;
    }


    private void UpdateValue(Vector3 newPos)
    {
        

        // calcualte value from pos

        float distMin = Vector3.Distance(newPos, minPosition.position);
        float range = Vector3.Distance(minPosition.position, maxPosition.position);

        float multiplier = distMin / range;
        value = multiplier * (max - min);
    }


    private float Map(float value)
    {
        if(value < min)
        {
            return min;
        }

        if(value > max)
        {
            return max;
        }

        value = value - min;
        float range = max - min;

        return value / range;
    }

}
