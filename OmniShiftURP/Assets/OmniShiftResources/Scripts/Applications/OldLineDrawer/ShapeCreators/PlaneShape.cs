using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlaneShape : Shape
{
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    

    public override GameObject CreateShape(Vector3[] points, Transform objectParent)
    {
        Bounds bounds = GeometryUtility.CalculateBounds(points, transform.localToWorldMatrix);

        //for plane y and z need to be switched
        // also need to downscale since plane size 1 is 10 times of a cube
        bounds.size = new Vector3(bounds.size.x, bounds.size.z, bounds.size.y) * 0.1f;


        GameObject tmpObj = Instantiate(shapePrefab, bounds.center, shapePrefab.transform.rotation, objectParent);
        tmpObj.transform.localScale = bounds.size;

        return tmpObj;
    }
}
