using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;

public class TileGenerator : MonoBehaviour
{
    public bool pythonCommunicationOff;

    [Serializable]
    public struct Test
    {
        public Vector3 testPos;
        public GameObject testPrefab;
        public Transform parent;
        public Vector3[] vertices;
        public Vector3 scale;
    }

    public Test[] tests;



    // Start is called before the first frame update
    void Start()
    {
        if (pythonCommunicationOff)
        {
            foreach (Test t in tests)
            {
                GameObject tile = CreateTile(t.testPrefab, t.parent, t.testPos);
                UpdateTile(tile, t.vertices, t.scale);
            }

            
        }
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    /// <summary>
    /// This creates a gameobject with the material and collider of the prefab and uses the given vertices to create the mesh.
    /// 
    /// </summary>
    /// <param name="prefab">This is used to define material of the instantiated mesh object</param>
    /// <param name="pos">The position where the object will be spawned</param>
    /// <param name="vertices">The dimensions/vertices of the mesh that will be instantiated on the object</param>
    /// <returns></returns>
    public static GameObject CreateTile(GameObject prefab, Transform parent, Vector3 pos)
    {
        GameObject tile = new GameObject();
        tile.transform.position = pos;
        tile.transform.parent = parent;

        // instantiate necessary components
        tile.gameObject.name = prefab.gameObject.name;
        MeshFilter filter = tile.AddComponent<MeshFilter>();
        MeshRenderer rend = tile.AddComponent<MeshRenderer>();
        //MeshCollider col = tile.AddComponent<MeshCollider>();
        //col.convex = true;
        //col.isTrigger = true;
        
        MeshGenerator gen = tile.AddComponent<MeshGenerator>();

        // Update attributes
        rend.sharedMaterial = prefab.GetComponentInChildren<MeshRenderer>().sharedMaterial;
        
        return tile;
    }


    public static void UpdateTile(GameObject tile, Vector3[] vertices, Vector3 scale)
    {
        //tile.transform.position = pos;
        MeshGenerator gen = tile.GetComponent<MeshGenerator>();
        gen.CreateMesh(vertices, scale);
    }


    private static T CopyComponent<T>(T original, GameObject destination) where T : Component
    {
        System.Type type = original.GetType();
        Component copy = destination.AddComponent(type);

        BindingFlags flags = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Default | BindingFlags.DeclaredOnly;


        PropertyInfo[] pinfos = type.GetProperties();
        foreach (PropertyInfo pInfo in pinfos)
        {
            if (pInfo.CanWrite)
            {
                //Debug.Log("Info " + pInfo.Name + "; value: " + pInfo.GetValue(original));
                pInfo.SetValue(copy, pInfo.GetValue(original, null), null);
            }
        }

        System.Reflection.FieldInfo[] fields = type.GetFields();
        foreach (System.Reflection.FieldInfo field in fields)
        {
            //Debug.Log("Field " + field.Name + "; value: " + field.GetValue(original));
            field.SetValue(copy, field.GetValue(original));
        }

        return copy as T;
    }
    

}
