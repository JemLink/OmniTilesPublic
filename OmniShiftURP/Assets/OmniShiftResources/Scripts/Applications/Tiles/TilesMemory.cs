using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TilesMemory : MonoBehaviour
{
    public List<int> formerTiles;



    public static TilesMemory Instance { get; private set; }

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(this);
        }
        else
        {
            Instance = this;
        }
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
