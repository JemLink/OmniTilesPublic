using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class WebbedHandTest : HandBehavior
{
    /*
     * Mediapipes indexing is as follows:
     * 0: wrist                     13: ring_MCP
     * 1: thumb_CMC                 14: ring_PIP
     * 2: thumb_MCP                 15: ring_DIP
     * 3: thumb_IP                  16: ring_TIP
     * 4: thumb_TIP                 17: pinky_MCP
     * 5: index_MCP                 18: pinky_PIP
     * 6: index_PIP                 19: pinky_DIP
     * 7: index_DIP                 20: pinky_TIP
     * 8: index_TIP
     * 9: middle_MCP
     * 10: middle_PIP
     * 11: middle_DIP
     * 12: middle_TIP
     * 
     * */

    public GameObject testImage;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (active)
        {
            DisplayImageBetweenFingers();
        }
    }

    public void DisplayImageBetweenFingers()
    {
        Hand closestHand = GetNextHand();

        // if there is no hand: move randomly
        if (closestHand == null)
        {
            // do nothing
        }
        else
        {
            DisplayImage(closestHand, 7, 11);
        }
    }

    /// <summary>
    /// This displays an image between the 2 given joints
    /// Mediapipes indexing is as follows:
    /// 0: wrist                     13: ring_MCP
    /// 1: thumb_CMC                 14: ring_PIP
    /// 2: thumb_MCP                 15: ring_DIP
    /// 3: thumb_IP                  16: ring_TIP
    /// 4: thumb_TIP                 17: pinky_MCP
    /// 5: index_MCP                 18: pinky_PIP
    /// 6: index_PIP                 19: pinky_DIP
    /// 7: index_DIP                 20: pinky_TIP
    /// 8: index_TIP
    /// 9: middle_MCP
    /// 10: middle_PIP
    /// 11: middle_DIP
    /// 12: middle_TIP
    /// </summary>
    /// <param name="hand"></param>
    /// <param name="jointIndx1"></param>
    /// <param name="jointIndex2"></param>
    private void DisplayImage(Hand hand, int jointIndex1, int jointIndex2)
    {
        if(hand.gesture == Hand.Gesture.Open)
        {
            testImage.GetComponent<Renderer>().enabled = true;
            Vector3 imagePos = hand.jointsRep[jointIndex1].transform.position + 0.5f * (hand.jointsRep[jointIndex2].transform.position - hand.jointsRep[jointIndex1].transform.position);
            imagePos =
            testImage.transform.position = imagePos;
        }
        else
        {
            testImage.GetComponent<Renderer>().enabled = false;
        }
        
    }
}
