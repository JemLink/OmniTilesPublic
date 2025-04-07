using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Triangle : TileShape
{
    public Triangle() { }

    public Triangle(int id)
    {
        this.id = id;
    }

    public Triangle(int id, Vector3 center, Vector3 rotation)
    {
        this.id = id;
        transform.position = center;
        transform.rotation = Quaternion.Euler(rotation);
    }


    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    
}
