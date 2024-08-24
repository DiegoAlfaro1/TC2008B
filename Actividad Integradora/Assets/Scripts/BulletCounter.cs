using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class BulletCounter : MonoBehaviour
{
    public TMP_Text bulletText;  // Cambiado a TMP_Text
    private int bulletBigCount;
    private int bulletMediumCount;
    private int bulletSmallCount;
    private int bulletCount;

    void Update()
    {
        bulletSmallCount = GameObject.FindGameObjectsWithTag("BulletSmall").Length;
        bulletMediumCount = GameObject.FindGameObjectsWithTag("BulletMedium").Length;
        bulletBigCount = GameObject.FindGameObjectsWithTag("BulletBig").Length;
        bulletCount = bulletBigCount + bulletMediumCount + bulletSmallCount;
        bulletText.text = "Bullets: " + bulletCount;
    }
}
