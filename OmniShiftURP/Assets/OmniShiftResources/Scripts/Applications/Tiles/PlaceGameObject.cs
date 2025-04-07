using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlaceGameObject : MonoBehaviour
{
    // make this a singleton since w do not want more placement than necessary
    private static PlaceGameObject _instance;
    public static PlaceGameObject Instance { get { return _instance; } }


    [Serializable]
    public struct ObjectID
    {
        public int ID;
        public GameObject objectPrefab;
    }

    public int startID;
    [Tooltip("Use this to assign GameObject for certain tile ids which will then be instantiated as a child of the tile")]
    public ObjectID[] objectsWithID;


    public Dictionary<int, GameObject> objectDict = new Dictionary<int, GameObject>();

    private void Awake()
    {

        // singleton behaviour
        if (_instance != null && _instance != this)
        {
            Destroy(this.gameObject);
        }
        else
        {
            _instance = this;
        }

    }

    private void OnValidate()
    {


        // assign ids since we only want one object per tile
        for (int i = 0; i < objectsWithID.Length; i++)
        {
            objectsWithID[i].ID = startID + i;
        }
    }


    // Start is called before the first frame update
    void Start()
    {
        objectDict = new Dictionary<int, GameObject>();

        for (int i = 0; i < objectsWithID.Length; i++)
        {
            objectDict.Add(objectsWithID[i].ID, objectsWithID[i].objectPrefab);
        }
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void AssignObjects(List<TileShape> tiles)
    {
        foreach(TileShape tile in tiles)
        {
            if (objectDict.ContainsKey(tile.id))
            {
                if (!tile.GetComponentInChildren<TileBehavior>())
                {
                    GameObject childObj = Instantiate(objectDict[tile.id], tile.transform);
                }
                else
                {
                    if(tile.GetComponentInChildren<TileBehavior>().ID != tile.id)
                    {
                        Debug.Log("Destroyed and reset");
                        Destroy(tile.GetComponentInChildren<TileBehavior>().gameObject);
                        GameObject childObj = Instantiate(objectDict[tile.id], tile.transform);

                    }
                }
                
            }
        }
        
    }
}
