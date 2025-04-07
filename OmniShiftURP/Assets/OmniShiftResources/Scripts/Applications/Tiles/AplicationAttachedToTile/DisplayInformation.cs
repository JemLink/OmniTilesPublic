using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DisplayInformation : TileBehavior
{
    public bool connected;
    public Renderer rend;

    // Start is called before the first frame update
    void Awake()
    {
        if (GetComponentInParent<TileShape>())
        {
            ID = GetComponentInParent<TileShape>().id;
        }

        if (!rend)
        {
            rend = GetComponentInChildren<Renderer>();
            rend.enabled = true;
        }

    }

    // Update is called once per frame
    void Update()
    {
        
    }

    

    //private void OnTriggerEnter(Collider other)
    //{
    //    if(other.gameObject.tag == "Country" && !connected)
    //    {
    //        Texture text = other.GetComponent<Renderer>().material.GetTexture("_BaseMap");
    //        if (text && rend)
    //        {
    //            rend.enabled = true;
    //            rend.material.SetTexture("_BaseMap", text);
                
    //        }
            
    //    }

    //    if (other.GetComponentInChildren<TileShape>())
    //    {
    //        connected = true;
    //        rend.enabled = false;
    //    }
    //}

    //private void OnTriggerExit(Collider other)
    //{
    //    if (other.GetComponentInChildren<TileShape>())
    //    {
    //        rend.enabled = true;
    //    }

    //    if(other.gameObject.tag == "Country")
    //    {
    //        connected = false;
    //        rend.enabled = false;
    //    }
        
    //}

    

    private void OnTriggerStay(Collider other)
    {
        if (other.gameObject.tag == "Country")
        {
            Texture text = other.GetComponent<Renderer>().material.GetTexture("_BaseMap");
            if (text && rend)
            {
                rend.enabled = true;
                rend.material.SetTexture("_BaseMap", text);

            }

        }

        if (other.GetComponentInChildren<TileShape>())
        {
            connected = true;
            rend.enabled = false;
        }

        //if (!connected)
        //{
        //    if (other.gameObject.tag == "Country" && !connected)
        //    {
        //        Texture text = other.GetComponent<Renderer>().material.GetTexture("_BaseMap");
        //        if (text && rend)
        //        {
        //            rend.enabled = true;
        //            rend.material.SetTexture("_BaseMap", text);

        //        }

        //    }
        //}
    }


}
