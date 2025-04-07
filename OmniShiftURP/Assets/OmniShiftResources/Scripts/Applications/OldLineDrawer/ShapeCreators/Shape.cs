using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public abstract class Shape : MonoBehaviour
{
    public GameObject shapePrefab;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    //public abstract GameObject CreateShape(Vector3[] points);
    public abstract GameObject CreateShape(Vector3[] points, Transform parent);
}
