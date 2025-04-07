using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public abstract class GravityAffected : MonoBehaviour
{
    public GravityOrbit gravityField;
    protected Transform parent;

    // Start is called before the first frame update
    protected void Start()
    {
        if (gravityField == null)
        {
            if (GameObject.FindGameObjectWithTag("GravityField"))
            {
                //Debug.Log("Attached gravity field: " + GameObject.FindGameObjectWithTag("GravityField").name);
                gravityField = GameObject.FindGameObjectWithTag("GravityField").GetComponent<GravityOrbit>();
            }
        }

        
    }

    protected void Awake()
    {
        if (gravityField == null)
        {
            if (GameObject.FindGameObjectWithTag("GravityField"))
            {
                Debug.Log("Attached gravity field: " + GameObject.FindGameObjectWithTag("GravityField").name);
                gravityField = GameObject.FindGameObjectWithTag("GravityField").GetComponent<GravityOrbit>();
            }
            
        }
    }
    

    // Update is called once per frame
    void Update()
    {
        
    }
}
