using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;


[System.Serializable]
public class ConnectionEvent : UnityEvent<GameObject, int> { }

[System.Serializable]
public class DisconnectionEvent : UnityEvent<GameObject, int> { }


/// <summary>
/// This script should be attached to the gameObject that will be attached as a child to the tile.
/// It is not an application script!
/// </summary>
public class SimpleConnection : TileBehavior
{
    [Serializable]
    public struct ChangingObjects
    {
        public int tileID;
        public GameObject changeTo;
        public bool shouldDisappear;
        public bool otherShouldDisappear;
    }

    

    [Tooltip("Use this to assign a behaviour that this gameobject/tile should have near other tiles")]
    public ChangingObjects[] changingObjects;


    public Dictionary<int, GameObject> objectDict = new Dictionary<int, GameObject>();
    public Dictionary<int, bool> objectDisappearance = new Dictionary<int, bool>();
    public Dictionary<int, bool> otherObjectDisappearance = new Dictionary<int, bool>();


    public ConnectionEvent connectionEvent;
    public DisconnectionEvent disconnectionEvent;

    private bool changed = false;
    /// <summary>
    /// When not changed the id is -1.
    /// Otherwise the id is the id of th object it changed with
    /// </summary>
    private int changedWith = -1;
    private Dictionary<int, GameObject> instantiatedObjs;

    


    // Start is called before the first frame update
    void Start()
    {
        objectDict = new Dictionary<int, GameObject>();

        for (int i = 0; i < changingObjects.Length; i++)
        {
            objectDict.Add(changingObjects[i].tileID, changingObjects[i].changeTo);
            objectDisappearance.Add(changingObjects[i].tileID, changingObjects[i].shouldDisappear);
            otherObjectDisappearance.Add(changingObjects[i].tileID, changingObjects[i].otherShouldDisappear);
        }

        instantiatedObjs = new Dictionary<int, GameObject>();

        if (GetComponentInParent<TileShape>())
        {
            ID = GetComponentInParent<TileShape>().id;
        }

    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnTriggerEnter(Collider other)
    {
        
        if (!changed)
        {
            TileShape tile = other.gameObject.GetComponentInChildren<TileShape>();
            Transform tmpTrans = other.gameObject.transform;
            while (!tile && tmpTrans)
            {
                tile = tmpTrans.GetComponentInChildren<TileShape>();
                tmpTrans = tmpTrans.parent;
            }
            
            if (tile && changedWith == -1 && objectDict.ContainsKey(tile.id))
            {
                // connect
                connectionEvent.Invoke(other.gameObject, tile.id);
            }
        }
        
    }

    private void OnTriggerExit(Collider other)
    {
        
        if (changed)
        {
            TileShape tile = other.gameObject.GetComponentInChildren<TileShape>();
            Transform tmpTrans = other.gameObject.transform;
            while (!tile && tmpTrans)
            {
                tmpTrans = tmpTrans.parent;
                tile = tmpTrans.GetComponentInChildren<TileShape>();
            }

            if (tile && changedWith == tile.id && objectDict.ContainsKey(tile.id))
            {
                // disconnect
                disconnectionEvent.Invoke(other.gameObject, tile.id);
            }
        }
    }


    public void CombineObjects(GameObject otherObject, int id)
    {
        if (!changed)
        {
            
            if (objectDisappearance[id])
            {
                SetAllRendererTo(GetComponentInParent<TileShape>().gameObject, false);
                //SetAllRendererTo(gameObject, false);
            }

            
            // check if the object should disappear with the other or stay
            if (otherObjectDisappearance[id])
            {
                SetAllRendererTo(otherObject.GetComponentInParent<TileShape>().gameObject, false);
            }
            
            changed = true;
            changedWith = id;

            if (instantiatedObjs.ContainsKey(id))
            {
                SetAllRendererTo(instantiatedObjs[id], true);
            }
            else
            {
                GameObject newObj = Instantiate(objectDict[id], transform.position, transform.rotation, transform);
                SetAllRendererTo(newObj, true);
                instantiatedObjs.Add(id, newObj);
            }

        }
        
    }


    public void SeparateObjects(GameObject otherObject, int id)
    {
        if (changed)
        {
            Debug.Log("Disconnect");
            SetAllRendererTo(GetComponentInParent<TileShape>().gameObject, true);
            SetAllRendererTo(otherObject.GetComponentInParent<TileShape>().gameObject, true);
            changed = false;
            changedWith = -1;

            if (instantiatedObjs.ContainsKey(id))
            {
                GameObject tmpObj = instantiatedObjs[id];
                instantiatedObjs.Remove(id);
                Destroy(tmpObj);
            }

        }
    }


    private void SetAllRendererTo(GameObject obj, bool enabled)
    {
        Renderer[] rends = obj.GetComponentsInChildren<Renderer>();

        for(int i = 0; i < rends.Length; i++)
        {
            rends[i].enabled = enabled;
        }
    }
    

}
