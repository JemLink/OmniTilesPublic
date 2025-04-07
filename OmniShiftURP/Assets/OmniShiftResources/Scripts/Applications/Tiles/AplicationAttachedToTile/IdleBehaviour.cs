using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class IdleBehaviour : TileBehavior
{
    // Start is called before the first frame update
    void Start()
    {
        if (GetComponentInParent<TileShape>())
        {
            ID = GetComponentInParent<TileShape>().id;
        }
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
